import time

import numpy as np
from pynq import Overlay
from pynq import allocate


class SevqOverlay(Overlay):
    MAX_N_OF_RECORDS = 800

    @classmethod
    def load(cls):
        return cls("/home/xilinx/overlays/sevq/overlay.bit")

    def __init__(self, bitfile, **kwargs):
        super().__init__(bitfile, **kwargs)

    def send(self, in_buffer, out_buffer):
        self.axi_dma.sendchannel.transfer(in_buffer)
        self.axi_dma.recvchannel.transfer(out_buffer)
        self.hls_code.write(0x0, 0x81)
        self.axi_dma.sendchannel.wait()
        self.axi_dma.recvchannel.wait()

    def reset(self):
        reset_data = np.array([-1, -1])
        with allocate(shape=(reset_data.shape[0],), dtype=np.int32) as in_buffer, \
                allocate(shape=(1,), dtype=np.int32) as out_buffer:
            np.copyto(in_buffer, reset_data)
            self.send(in_buffer, out_buffer)
            result = out_buffer.copy()
            if result[0] != 1:
                raise RuntimeError("SevqOverlay reset failed")

    def fit(self, x: np.ndarray, y: np.ndarray,
            n_decimal_places=6,  # only applied if not int
            epochs=10, permute=True, seed=1,
            return_elapsed_time=False
            ):

        if not np.issubdtype(x.dtype, np.integer):
            x = ((10 ** n_decimal_places) * x)

        x = x.astype(np.int32)
        y = np.atleast_2d(y).T.astype(np.int32)

        result = None
        elapsed_time = 0

        _x = x
        _y = y

        random_state = np.random.RandomState(seed=seed)

        for _ in range(epochs):
            if permute:
                idx = random_state.permutation(np.arange(len(x)))
                _x = x[idx]
                _y = y[idx]

            split_parts = (_x.shape[0] // self.MAX_N_OF_RECORDS) + 1
            x_chunks = np.array_split(_x, split_parts)
            y_chunks = np.array_split(_y, split_parts)

            for x_chunk, y_chunk in zip(x_chunks, y_chunks):
                xy_chunk = np.concatenate((x_chunk, y_chunk), axis=1).flatten()
                data = np.concatenate((x_chunk.shape, xy_chunk))
                with allocate(shape=(data.shape[0],), dtype=np.int32) as in_buffer, \
                        allocate(shape=(y_chunk.shape[0],), dtype=np.int32) as out_buffer:

                    np.copyto(in_buffer, data)

                    start = time.time()

                    self.send(in_buffer, out_buffer)

                    elapsed_time += time.time() - start

                    if result is not None:
                        result = np.concatenate((result, out_buffer.copy()))
                    else:
                        result = out_buffer.copy()

        if return_elapsed_time:
            return result, elapsed_time
        return result

    def predict(self, x: np.ndarray,
                n_decimal_places=6,  # only applied if not int
                return_elapsed_time=False
                ):

        y = np.zeros(x.shape[0]) - 1  # set all y to -1, it will not fit only predict
        return self.fit(
            x, y, n_decimal_places=n_decimal_places,
            epochs=1, permute=False,
            return_elapsed_time=return_elapsed_time
        )


class SevqOverlay2(Overlay):
    MAX_N_OF_RECORDS = 200

    @classmethod
    def load(cls, n_attrs):
        return cls("/home/xilinx/overlays/sevq/overlay.bit", n_attrs)

    def __init__(self, bitfile, n_attrs, **kwargs):
        super().__init__(bitfile, **kwargs)
        self.n_attrs = n_attrs
        self.unique_labels = set()

    def __enter__(self):
        print('__enter__', flush=True)
        self.in_buffer = allocate(shape=(2 + self.n_attrs + 1,), dtype=np.int32)
        self.out_buffer = allocate(shape=(1,), dtype=np.int32)
        print('__enter__ 2', flush=True)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('__exit__', flush=True)
        self.in_buffer.close()
        self.out_buffer.close()

    def send(self, data, n_decimal_places=6):
        if not np.issubdtype(data.dtype, np.integer):
            data[2:-1] = ((10 ** n_decimal_places) * data[2:-1])

        data = data.astype(np.int32)
        np.copyto(self.in_buffer, data)

        self.axi_dma.sendchannel.transfer(self.in_buffer)
        self.axi_dma.recvchannel.transfer(self.out_buffer)
        self.hls_code.write(0x0, 0x81)
        self.axi_dma.sendchannel.wait()
        self.axi_dma.recvchannel.wait()

        return self.out_buffer.copy()

    def learn_one(self, x: dict, y, **kwargs):
        self.unique_labels.add(y)
        x = np.fromiter(x.values(), dtype=float)
        data = np.concatenate(((1, self.n_attrs), x, (y,)))
        return self.send(data)[0]

    def predict_proba_one(self, x: dict):
        proba = {c: 0. for c in sorted(self.unique_labels)}
        x = np.fromiter(x.values(), dtype=float)
        data = np.concatenate(((1, self.n_attrs), x, (-1,)))
        pred = self.send(data)[0]
        if pred != -1:
            proba[pred] = 1.
        return proba
