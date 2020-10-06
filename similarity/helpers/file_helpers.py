import codecs
import h5py


def load_file_content(file_path):
    with codecs.open(file_path, encoding='utf-8') as f:
        return f.read()


def save_array_as_h5(data, file_path):
    with h5py.File(file_path, 'w') as f:
        f.create_dataset('data_set', data=data)


def load_array_h5_file(file_path):
    with h5py.File(file_path, 'r') as f:
        return f['data_set'][:]
