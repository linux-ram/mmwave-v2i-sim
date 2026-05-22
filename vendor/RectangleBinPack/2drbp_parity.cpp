#include <cstdio>
#include <cstdlib>
#include <vector>

#include "GuillotineBinPack.h"

int main(int argc, char** argv) {
    if (argc < 5) {
        return 1;
    }
    int bw = atoi(argv[1]);
    int bh = atoi(argv[2]);
    rbp::GuillotineBinPack pack(bw, bh);
    std::vector<int> unpacked;
    for (int i = 3; i + 1 < argc; i += 2) {
        int iw = atoi(argv[i]);
        int ih = atoi(argv[i + 1]);
        rbp::Rect r = pack.Insert(
            iw,
            ih,
            true,
            rbp::GuillotineBinPack::RectBestShortSideFit,
            rbp::GuillotineBinPack::SplitShorterLeftoverAxis);
        if (i > 3) {
            printf(" ");
        }
        if (r.width == 0 || r.height == 0) {
            printf("-1 -1 -1 -1");
            unpacked.push_back((i - 3) / 2 + 1);
        } else {
            printf("%d %d %d %d", r.x, r.y, r.width, r.height);
        }
    }
    printf("\nUNPACKED");
    for (size_t i = 0; i < unpacked.size(); ++i) {
        printf(" %d", unpacked[i]);
    }
    printf("\n");
    return 0;
}
