#include "ap_axi_sdata.h"
#include "hls_stream.h"
#include <limits>

#define MAX_N_OF_RECORDS 800
#define MAX_N_OF_ATTRS 40
#define MAX_N_OF_CATEGORIES 2000
#define UNKNOWN_LABEL -1


typedef ap_axis<32, 2, 5, 6> transfer_type;
typedef hls::stream<transfer_type> transfer_stream;

void top(transfer_stream &in_stream, transfer_stream &out_stream);
