import dataclasses
import ssl
import typing
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from urllib.request import urlretrieve
from zipfile import ZipFile

import numpy as np
import pandas as pd
import typing_extensions
from sklearn import preprocessing
from tqdm import tqdm

BASE_KEEL_URL = 'https://sci2s.ugr.es/keel/dataset/data/classification/'

AVAILABLE_N_FOLDS = typing_extensions.Literal[5, 10]


@dataclasses.dataclass
class ClassificationFoldData:
    """
    Class that represents single dataset fold.
    """

    index: int = dataclasses.field()
    labels: np.ndarray = dataclasses.field()

    x_train: np.ndarray = dataclasses.field(repr=False)
    y_train: np.ndarray = dataclasses.field(repr=False)
    x_test: np.ndarray = dataclasses.field(repr=False)
    y_test: np.ndarray = dataclasses.field(repr=False)


class ClassificationFoldDataModifierBase(ABC):

    @abstractmethod
    def modify(self, fold: ClassificationFoldData) -> ClassificationFoldData:
        pass


class ClassificationFoldDataNormalizer(ClassificationFoldDataModifierBase):

    def modify(self, fold: ClassificationFoldData) -> ClassificationFoldData:
        x_tra_len = len(fold.x_train)
        x = np.concatenate([fold.x_train.astype(float), fold.x_test.astype(float)])
        min_max_scaler = preprocessing.MinMaxScaler()
        x = min_max_scaler.fit_transform(x)
        x_train, x_test = x[:x_tra_len], x[x_tra_len:]
        return ClassificationFoldData(
            index=fold.index,
            labels=fold.labels,
            x_train=x_train,
            y_train=fold.y_train,
            x_test=x_test,
            y_test=fold.y_test
        )


class ClassificationDatasetBase(ABC):
    """
    Base class for classification dataset that represents single dataset.
    """

    def __init__(self, seed=1):
        self.seed = seed

    @abstractmethod
    def folds(
            self,
            n_folds: AVAILABLE_N_FOLDS = 10,
            dob_scv: bool = True,
            categorical_to_numerical=True
    ) -> typing.Iterable[ClassificationFoldData]:
        pass

    def __iter__(self):
        random_state = np.random.RandomState(seed=self.seed)
        for fold in self.folds():
            idx = random_state.permutation(np.arange(len(fold.x_test)))
            x_test = fold.x_test[idx]
            y_test = fold.y_test[idx]
            for x_data, y in zip(x_test, y_test):
                x = {i: value for i, value in enumerate(x_data)}
                yield x, y

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def instances(self) -> int:
        pass

    @property
    @abstractmethod
    def features(self) -> int:
        pass

    @property
    @abstractmethod
    def classes(self) -> int:
        pass

    def __str__(self):
        return f'Dataset name: {self.name}, ' \
               f'instances: {self.instances}, ' \
               f'features: {self.features}, ' \
               f'classes: {self.classes}'


class DatasetDescriptionFields(str, Enum):
    Inputs = "@inputs"
    Outputs = "@outputs"


class ClassificationDatasetDownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, t_size=None):
        if t_size is not None:
            self.total = t_size
        self.update(b * bsize - self.n)


class ClassificationDataset(ClassificationDatasetBase):
    """
    Class that represents KEEL single dataset.
    """

    def __init__(self, name: str,
                 files_cache_path=Path.home().joinpath('cacp_files'),
                 seed=1):
        """
        Initializes class instance that represents KEEL single dataset.

        :param name: KEEL dataset name
        :param files_cache_path: optional cache file patch where dataset will be downloaded
        """

        super().__init__(seed)

        self._name = name

        self._instances = 0
        self._features = 0
        self._classes = 0

        self._output = 'Class'
        self._origin = ''
        self._attributes: typing.Dict[str, str] = {}

        self._files_cache_path = files_cache_path
        self._files_cache_path.mkdir(exist_ok=True, parents=True)

        self._load_description()

    @property
    def name(self) -> str:
        return self._name

    @property
    def instances(self) -> int:
        return self._instances

    @property
    def features(self) -> int:
        return self._features

    @property
    def classes(self) -> int:
        return self._classes

    @property
    def origin(self) -> str:
        return self._origin

    @property
    def output_name(self) -> str:
        return self._output_name

    def folds(
            self,
            n_folds: AVAILABLE_N_FOLDS = 10,
            dob_scv: bool = True,
            categorical_to_numerical=True
    ) -> typing.Iterable[ClassificationFoldData]:

        zip_data_name = f'{self.name}-{n_folds}-{"dobscv" if dob_scv else "fold"}'
        data_path = self._fetch_data(zip_data_name, dob_scv)
        if dob_scv:
            data_name = f'{self.name}-{n_folds}dobscv'
        else:
            data_name = f'{self.name}-{n_folds}'

        for fold_index in range(1, n_folds + 1):
            train_data_path = data_path.joinpath(f'{data_name}-{fold_index}tra.dat')
            x_tra, y_tra = self._load_data(train_data_path, categorical_to_numerical)

            test_data_path = data_path.joinpath(f'{data_name}-{fold_index}tst.dat')
            x_tst, y_tst = self._load_data(test_data_path, categorical_to_numerical)

            labels = np.unique(np.hstack([y_tra, y_tst]))

            yield ClassificationFoldData(
                index=fold_index,
                x_train=x_tra,
                y_train=y_tra,
                x_test=x_tst,
                y_test=y_tst,
                labels=labels
            )

    def _load_description(self):
        file_name = f'{self.name}-names.txt'
        file_path = self._fetch_file(file_name)

        attributes_names = []
        attributes_types_names = []
        inputs = []
        output_name = 'Class'
        # KEEL descriptions files contain latin1 chars
        with file_path.open('r', encoding='latin1') as file:
            for line in file:
                if '@attribute' in line or '@Attribute' in line:
                    if '{' in line:
                        attr_name = line.split('{')[0].split()[1]
                        attr_type = 'category'
                    else:
                        s = line.split()[1:]
                        attr_name = s[0].strip()
                        attr_type = s[1].split('[')[0].strip()
                    attributes_names.append(attr_name)
                    attributes_types_names.append(attr_type)
                if '@input' in line:
                    inputs.append(line.split()[1:])
                elif '@output' in line:
                    output_name = line.split()[1]
                elif 'Origin.' in line:
                    self._origin = line.split('Origin.')[1].strip()
                elif 'Features.' in line:
                    self._features = int(line.split('Features.')[1].strip())
                elif 'Classes.' in line:
                    self._classes = int(line.split('Classes.')[1].strip())
                elif 'Instances.' in line:
                    self._instances = int(line.split('Instances.')[1].split()[0].strip())

        self._attributes = {n: t for n, t in zip(attributes_names, attributes_types_names)}
        self._output_name = output_name

    def _load_data(self, path: Path, categorical_to_numerical: bool) -> typing.Tuple[np.ndarray, np.ndarray]:
        skip_rows = 4 + len(self._attributes)
        df = pd.read_csv(path, skiprows=skip_rows, names=self._attributes.keys(), na_values='?')
        if categorical_to_numerical:
            for attr_name, attr_type_name in self._attributes.items():
                if attr_type_name == 'category':
                    df[attr_name] = df[attr_name].astype('category').cat.codes.values

        y = df[self._output_name].values
        del df[self._output_name]
        x = df.values
        return x, y

    def _fetch_data(self, data_name: str, dob_scv: bool) -> Path:
        data_path = self._files_cache_path.joinpath(data_name)
        data_unzip_path = data_path
        if dob_scv:
            data_path = data_path.joinpath(self.name)
            data_unzip_path = data_path.parent

        if not data_path.exists():
            zip_file_path = self._fetch_file(f'{data_name}.zip')
            with ZipFile(zip_file_path, mode='r') as zipfile:
                zipfile.extractall(data_unzip_path)
        return data_path

    def _fetch_file(self, file_name: str) -> Path:
        out_file_path = self._files_cache_path.joinpath(file_name)
        if not out_file_path.exists():
            url = f'{BASE_KEEL_URL}{file_name}'
            # KEEL page sometimes fails on ssl cert (we can not fix it)
            ssl._create_default_https_context = ssl._create_unverified_context
            with ClassificationDatasetDownloadProgressBar(unit='B', unit_scale=True, miniters=1,
                                                          desc=f'Downloading {file_name}') as t:
                urlretrieve(url, filename=out_file_path, reporthook=t.update_to)

        return out_file_path
