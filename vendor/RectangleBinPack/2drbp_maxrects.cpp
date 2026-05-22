// MaxRects Best-Area-Fit packer CLI harness (mirrors 2drbp_parity interface).
// Usage: 2drbp_maxrects <bin_w> <bin_h> [w h ...]
// Stdout line 1: "x y w h ..." for each placed rect
// Stdout line 2: "UNPACKED [id ...]"

#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <limits>
#include <utility>
#include <vector>

struct Rect {
    int x, y, w, h;
};

struct Item {
    int id, w, h;
};

static bool rects_intersect(const Rect& a, const Rect& b) {
    return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
}

static bool a_contains_b(const Rect& a, const Rect& b) {
    return a.x <= b.x && a.y <= b.y && a.x + a.w >= b.x + b.w && a.y + a.h >= b.y + b.h;
}

static void prune_contained(std::vector<Rect>& free) {
    std::vector<Rect> result;
    for (size_t i = 0; i < free.size(); ++i) {
        bool dominated = false;
        for (size_t j = 0; j < free.size(); ++j) {
            if (i == j) {
                continue;
            }
            if (a_contains_b(free[j], free[i]) && !(free[j].x == free[i].x && free[j].y == free[i].y && free[j].w == free[i].w && free[j].h == free[i].h)) {
                dominated = true;
                break;
            }
            if (a_contains_b(free[j], free[i]) && j < i) {
                dominated = true;
                break;
            }
        }
        if (!dominated) {
            result.push_back(free[i]);
        }
    }
    free = result;
}

int main(int argc, char** argv) {
    if (argc < 3) {
        return 1;
    }
    int bin_w = atoi(argv[1]);
    int bin_h = atoi(argv[2]);

    std::vector<Item> items;
    for (int i = 3; i + 1 < argc; i += 2) {
        items.push_back({(int)items.size() + 1, atoi(argv[i]), atoi(argv[i + 1])});
    }

    std::vector<Rect> free_rects = {{0, 0, bin_w, bin_h}};
    std::vector<Rect> placed;
    std::vector<int> unpacked_ids;

    for (auto& item : items) {
        int best_area = std::numeric_limits<int>::max();
        int best_fi = -1;
        int best_w = item.w, best_h = item.h;

        for (int fi = 0; fi < (int)free_rects.size(); ++fi) {
            const Rect& fr = free_rects[fi];
            for (int rot = 0; rot < 2; ++rot) {
                int w = rot == 0 ? item.w : item.h;
                int h = rot == 0 ? item.h : item.w;
                if (w <= fr.w && h <= fr.h) {
                    int area = fr.w * fr.h;
                    if (area < best_area) {
                        best_area = area;
                        best_fi = fi;
                        best_w = w;
                        best_h = h;
                    }
                }
            }
        }

        if (best_fi == -1) {
            unpacked_ids.push_back(item.id);
            continue;
        }

        int px = free_rects[best_fi].x;
        int py = free_rects[best_fi].y;
        Rect p = {px, py, best_w, best_h};
        placed.push_back(p);

        std::vector<Rect> new_free;
        for (const Rect& fr : free_rects) {
            if (rects_intersect(fr, p)) {
                if (fr.y < py) {
                    new_free.push_back({fr.x, fr.y, fr.w, py - fr.y});
                }
                if (fr.y + fr.h > py + best_h) {
                    new_free.push_back({fr.x, py + best_h, fr.w, fr.y + fr.h - py - best_h});
                }
                if (fr.x < px) {
                    new_free.push_back({fr.x, fr.y, px - fr.x, fr.h});
                }
                if (fr.x + fr.w > px + best_w) {
                    new_free.push_back({px + best_w, fr.y, fr.x + fr.w - px - best_w, fr.h});
                }
            } else {
                new_free.push_back(fr);
            }
        }
        prune_contained(new_free);
        free_rects = new_free;
    }

    for (size_t i = 0; i < placed.size(); ++i) {
        if (i) {
            printf(" ");
        }
        printf("%d %d %d %d", placed[i].x, placed[i].y, placed[i].w, placed[i].h);
    }
    printf("\nUNPACKED");
    for (int id : unpacked_ids) {
        printf(" %d", id);
    }
    printf("\n");
    return 0;
}
