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
    pack.Insert(
        rects,
        true,
        rbp::GuillotineBinPack::RectBestShortSideFit,
        rbp::GuillotineBinPack::SplitShorterLeftoverAxis);
    auto used = pack.GetUsedRectangles();
    for (size_t i = 0; i < used.size(); ++i) {
        if (i) {
            printf(" ");
        }
        printf("%d %d %d %d", used[i].x, used[i].y, used[i].width, used[i].height);
    }
    printf("\n");
    return 0;
}
