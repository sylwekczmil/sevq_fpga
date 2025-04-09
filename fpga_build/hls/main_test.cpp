#include <iostream>
#include "main.h"

using namespace std;

transfer_stream in_stream, out_stream;

transfer_type make_transfer_object() {
    transfer_type tmp;
    tmp.keep = 1;
    tmp.strb = 1;
    tmp.user = 1;
    tmp.id = 0;
    tmp.dest = 2;
    tmp.last = false;
    return tmp;
}

void write(const vector<int> &vec) {
    auto tmp = make_transfer_object();
    for (int i = 0; i < vec.size(); i++) {
        tmp.data = vec[i];
        tmp.last = (i == vec.size() - 1);
        in_stream.write(tmp);
    }
}

vector<int> read() {
    vector<int> vec{};
    auto tmp = make_transfer_object();
    do {
        tmp = out_stream.read();
        vec.push_back(tmp.data.to_int());
    } while (!tmp.last);

    return vec;
}

vector<int> write_read(const vector<int> &vec) {
    write(vec);
    top(in_stream, out_stream);
    return read();
}

int main() {


    vector<int> output = write_read({
                                            4, 2,
                                            -2, -2, 2,
                                            -1, -1, 1,
                                            1, 1, 1,
                                            2, 2, 2
                                    });

    vector<int> expected_output = {2, 1, 1, 2};
    if (output != expected_output) {
        cout << "Error: learning results do not match" << endl;
        return 1;
    }

    output = write_read({
                                1, 2,
                                -2, -2, 2
                        });

    expected_output = {2};
    if (output != expected_output) {
        cout << "Error: prediction results do not match" << endl;
        return 1;
    }

    output = write_read({
                                3, 2,
                                0, 0, UNKNOWN_LABEL,
                                3, 3, UNKNOWN_LABEL,
                                -3, -3, UNKNOWN_LABEL
                        });

    expected_output = {1, 2, 2};
    if (output != expected_output) {
        cout << "Error: prediction results do not match" << endl;
        return 1;
    }


    return 0;
}
