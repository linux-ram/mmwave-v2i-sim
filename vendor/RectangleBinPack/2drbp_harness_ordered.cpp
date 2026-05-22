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
    std::vector<rbp::RectSize> rects;
    for (int i = 3; i + 1 < argc; i += 2) {
        rbp::RectSize r;
        r.width = atoi(argv[i]);
        r.height = atoi(argv[i + 1]);
        rects.push_back(r);
    }
    int n = (int)rects.size();
    pack.Insert(
        rects,
        true,
        rbp::GuillotineBinPack::RectBestShortSideFit,
        rbp::GuillotineBinPack::SplitShorterLeftoverAxis);
    auto used = pack.GetUsedRectangles();
    for (int i = 0; i < n; ++i) {
        if (i) {
            printf(" ");
        }
        if (i < (int)used.size()) {
            printf("%d %d %d %d", used[i].x, used[i].y, used[i].width, used[i].height);
        } else {
            printf("-1 -1 -1 -1");
        }
    }
    printf("\n");
    return 0;
}
