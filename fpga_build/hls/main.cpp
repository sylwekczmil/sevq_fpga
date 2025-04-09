#include "main.h"

void top(transfer_stream &in_stream, transfer_stream &out_stream) {

#pragma HLS INTERFACE axis port=in_stream
#pragma HLS INTERFACE axis port=out_stream
#pragma hls interface s_axilite port=return

    transfer_type tmp;

    static int n_of_categories = 0;
    static int categories_weights[MAX_N_OF_CATEGORIES][MAX_N_OF_ATTRS];
    static int categories_labels[MAX_N_OF_CATEGORIES];
    static int categories_n_learns[MAX_N_OF_CATEGORIES];

    int value, record_idx, attribute_idx, category_idx;

    int distances[MAX_N_OF_CATEGORIES];
    int smallest_distance = INT_MAX, smallest_distance_idx = 0;

    int values[MAX_N_OF_RECORDS][MAX_N_OF_ATTRS];
    int labels[MAX_N_OF_RECORDS];

    tmp = in_stream.read();
    int n_of_records = tmp.data.to_int();
    tmp = in_stream.read();
    int n_of_attributes = tmp.data.to_int();

    if (n_of_records == -1 && n_of_attributes == -1) {
        // reset
        n_of_categories = 0;
        tmp.data = 1;
        tmp.last = true;
        out_stream.write(tmp);
        return;
    }

    record_idx = 0, attribute_idx = 0;
    do {
        tmp = in_stream.read();
        value = tmp.data.to_int();
        if (record_idx < n_of_records) {
            if (attribute_idx == n_of_attributes) { // is label value
                labels[record_idx] = value;
                attribute_idx = 0;
                record_idx++;
            } else { // is attribute value
                values[record_idx][attribute_idx] = value;
                attribute_idx++;
            }
        }


    } while (!tmp.last);


    for (record_idx = 0; record_idx < n_of_records; record_idx++) {

        // calculate distances to categories
        for (category_idx = 0; category_idx < n_of_categories; category_idx++) {
            distances[category_idx] = 0;
            for (attribute_idx = 0; attribute_idx < n_of_attributes; attribute_idx++) {
                int diff = categories_weights[category_idx][attribute_idx] - values[record_idx][attribute_idx];
                int abs_diff = diff < 0 ? diff * -1 : diff;
                distances[category_idx] += abs_diff;
            }
        }

        // find the closest distance and category idx
        smallest_distance = INT_MAX, smallest_distance_idx = 0;
        for (category_idx = 0; category_idx < n_of_categories; category_idx++) {
            if (distances[category_idx] < smallest_distance) {
                smallest_distance = distances[category_idx];
                smallest_distance_idx = category_idx;
            }
        }

        if (n_of_categories > 0) {
            if (labels[record_idx] == UNKNOWN_LABEL) { // predict
                labels[record_idx] = categories_labels[smallest_distance_idx];
            } else { // train
                if (labels[record_idx] != categories_labels[smallest_distance_idx]) {
                    if (n_of_categories + 1 < MAX_N_OF_CATEGORIES) {
                        // fill new category
                        for (attribute_idx = 0; attribute_idx < n_of_attributes; attribute_idx++) {
                            categories_weights[n_of_categories][attribute_idx] = values[record_idx][attribute_idx];
                        }
                        categories_labels[n_of_categories] = labels[record_idx];
                        categories_n_learns[n_of_categories] = 1;
                        n_of_categories++;
                    }

                } else { // update weights
                    categories_n_learns[smallest_distance_idx] += 1;
                    for (attribute_idx = 0; attribute_idx < n_of_attributes; attribute_idx++) {
                        categories_weights[smallest_distance_idx][attribute_idx] =
                                categories_weights[smallest_distance_idx][attribute_idx] + (
                                        (values[record_idx][attribute_idx] -
                                         categories_weights[smallest_distance_idx][attribute_idx]) /
                                        categories_n_learns[smallest_distance_idx]
                                );
                    }
                }
            }
        } else { // init first category
            for (attribute_idx = 0; attribute_idx < n_of_attributes; attribute_idx++) {
                categories_weights[n_of_categories][attribute_idx] = values[record_idx][attribute_idx];
            }
            categories_labels[n_of_categories] = labels[record_idx];
            categories_n_learns[n_of_categories] = 1;
            n_of_categories++;
        }

    }


    int last_ri = n_of_records - 1;
    for (record_idx = 0; record_idx < n_of_records; record_idx++) {
        tmp.data = labels[record_idx];
        tmp.last = (record_idx == last_ri);
        out_stream.write(tmp);
    }
}
