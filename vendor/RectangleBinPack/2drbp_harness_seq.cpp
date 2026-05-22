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
    std::vector<std::pair<int, int>> items;
    for (int i = 3; i + 1 < argc; i += 2) {
        items.push_back({atoi(argv[i]), atoi(argv[i + 1])});
    }
    for (size_t i = 0; i < items.size(); ++i) {
        if (i) {
            printf(" ");
        }
        rbp::Rect r = pack.Insert(
            items[i].first,
            items[i].second,
            true,
            rbp::GuillotineBinPack::RectBestShortSideFit,
            rbp::GuillotineBinPack::SplitShorterLeftoverAxis);
        if (r.width == 0 && r.height == 0) {
            printf("-1 -1 -1 -1");
        } else {
            printf("%d %d %d %d", r.x, r.y, r.width, r.height);
        }
    }
    printf("\n");
    return 0;
}
