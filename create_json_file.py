import json

def get_canvas_size(form, base, size):
    sizes = {
        "Квадрат": {
            "На картоне": {"Малый": ["7x7", "10x10", "15x15", "20x20"],
                           "Средний": ["30x30", "40x40"],
                           "Большой": ["50x50"]},
            "На подрамнике": {"Малый": ["10x10", "15x15", "20x20", "25x25"],
                              "Средний": ["30x30", "40x40"],
                              "Большой": ["50x50", "60x60", "70x70", "80x80", "100x100"]}
        },
        "Прямоугольник": {
            "На картоне": {"Малый": ["15x20", "18x24", "20x30"],
                           "Средний": ["25x30", "30x40", "40x50"],
                           "Большой": ["50x70"]},
            "На подрамнике": {"Малый": ["18x24", "20x30", "24x30"],
                              "Средний": ["25x35", "30x40", "40x50"],
                              "Большой": ["40x55", "40x60", "50x70", "60x100", "60x120", "100x150"]}
        },
        "Круг": {
            "На картоне": {"Малый": ["7,5", "10", "15", "18", "20", "24"],
                           "Средний": ["30", "40", "45"],
                           "Большой": ["50", "60", "70", "75"]},
            "На подрамнике": {"Малый": ["На магните", "На магните"],
                              "Средний": ["30", "35", "40"],
                              "Большой": ["50", "60"]}
        },
        "Овал": {
            "На картоне": {"Малый": ["20x30", "25x30"],
                           "Средний": ["30x40"],
                           "Большой": ["55x65"]},
            "На подрамнике": {"Малый": ["20x30", "25x35"],
                              "Средний": ["30x40", "40x50"],
                              "Большой": ["50x60"]}
        }
    }

    return sizes[form][base][size]


sizes = {
        "Квадрат": {
            "На картоне": {"Малый": ["7x7", "10x10", "15x15", "20x20"],
                           "Средний": ["30x30", "40x40"],
                           "Большой": ["50x50"]},
            "На подрамнике": {"Малый": ["10x10", "15x15", "20x20", "25x25"],
                              "Средний": ["30x30", "40x40"],
                              "Большой": ["50x50", "60x60", "70x70", "80x80", "100x100"]}
        },
        "Прямоугольник": {
            "На картоне": {"Малый": ["15x20", "18x24", "20x30"],
                           "Средний": ["25x30", "30x40", "40x50"],
                           "Большой": ["50x70"]},
            "На подрамнике": {"Малый": ["18x24", "20x30", "24x30"],
                              "Средний": ["25x35", "30x40", "40x50"],
                              "Большой": ["40x55", "40x60", "50x70", "60x100", "60x120", "100x150"]}
        },
        "Круг": {
            "На картоне": {"Малый": ["7,5", "10", "15", "18", "20", "24"],
                           "Средний": ["30", "40", "45"],
                           "Большой": ["50", "60", "70", "75"]},
            "На подрамнике": {"Малый": ["На магните", "На магните"],
                              "Средний": ["30", "35", "40"],
                              "Большой": ["50", "60"]}
        },
        "Овал": {
            "На картоне": {"Малый": ["20x30", "25x30"],
                           "Средний": ["30x40"],
                           "Большой": ["55x65"]},
            "На подрамнике": {"Малый": ["20x30", "25x35"],
                              "Средний": ["30x40", "40x50"],
                              "Большой": ["50x60"]}
        }
    }


with open('info.json', 'w') as f:
    json.dump(sizes, f)