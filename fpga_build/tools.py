import logging
import os
import subprocess
from functools import cached_property
from typing import Tuple

LOGGER = logging.Logger(__name__)
SUPPORTED_VITIS_AND_VIVADO_VERSION = 'v2020.2'


class FpgaBuildTools:

    def vitis_hls_run(self, command: str, capture_output=False, in_directory: str = None) -> Tuple[str, str]:
        return self.run(f'{self.vitis_hls_path} {command} -l ""', capture_output=capture_output, in_directory=in_directory)

    @cached_property
    def vitis_hls_path(self) -> str:
        return self.get_app_path('vitis_hls')

    def vivado_run(self, command: str, capture_output=False, in_directory: str = None) -> Tuple[str, str]:
        return self.run(f'{self.vivado_path} {command}', capture_output=capture_output, in_directory=in_directory)

    @cached_property
    def vivado_path(self) -> str:
        return self.get_app_path('vivado')

    @classmethod
    def get_app_path(cls, app_name) -> str:
        env_var_name = f'{app_name.upper()}_PATH'
        app_path = os.environ.get(env_var_name, app_name)
        out, err = cls.run(f'{app_path} -version -l ""')

        if err:
            raise Exception(f'Could not find {app_name} application under "{app_path}" path,'
                            f' set it up using {env_var_name} environment variable')

        if SUPPORTED_VITIS_AND_VIVADO_VERSION not in out:
            LOGGER.warning(
                f'Application {app_name} version differs from required one {SUPPORTED_VITIS_AND_VIVADO_VERSION},'
                f' it may cause problems while running this script. You are running version: \n{out}')

        return app_path

    @staticmethod
    def run(command: str, capture_output=True, in_directory: str = None) -> Tuple[str, str]:
        sc = command.split(' ')
        c = ['cd', in_directory, '&&'] + sc if in_directory else sc
        res = subprocess.run(c, capture_output=capture_output, shell=True)
        if capture_output:
            return res.stdout.decode("utf-8"), res.stderr.decode("utf-8")
        else:
            return '', ''
