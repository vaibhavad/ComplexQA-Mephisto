import plotly.graph_objects as go
import json

# FILE_NAME = 'hotpotqa_data.json'
# SUNBURST_PLOT_NAME = 'hotpotqa_sunburst_all_trigrams.pdf'
# MIN_VALUE = 250

FILE_NAME = 'final_complex_dataset.json'
SUNBURST_PLOT_NAME = 'final_complex_dataset_sunburst_all_trigrams.pdf'
MIN_VALUE = 5


def main(filename, sunburst_plot_name, min_value):
    count_dict = {}

    with open(filename, 'r') as f:
        data = json.load(f)
    for turn in data:
        question = turn['question']
        all_text = question.strip().strip('?.').lower().split()[:3]
        for j in range(len(all_text)-2):
            text = all_text[j:j+3]
            if len(text) >= 1:
                for i, word in enumerate(text):
                    if i == 0:
                        if word not in count_dict:
                            count_dict[word] = {"count": 0, "children": {}}
                        count_dict[word]["count"] += 1
                    elif i == 1:
                        if word not in count_dict[text[0]]["children"]:
                            count_dict[text[0]]["children"][word] = {"count": 0, "children": {}}
                        count_dict[text[0]]["children"][word]["count"] += 1
                    elif i == 2:
                        if word not in count_dict[text[0]]["children"][text[1]]["children"]:
                            count_dict[text[0]]["children"][text[1]]["children"][word] = {"count": 0, "children": {}}
                        count_dict[text[0]]["children"][text[1]]["children"][word]["count"] += 1

    charcter = [" "]
    parent = [""]
    values = [10000]
    ids = [""]

    for key, value in count_dict.items():
        if value["count"] >= MIN_VALUE:
            charcter.append(key)
            parent.append(" ")
            values.append(value["count"])
            ids.append(key)

    for key, value in count_dict.items():
        for key2, value in count_dict[key]["children"].items():
            if value["count"] >= MIN_VALUE:
                # while key2 in charcter:
                #     key2 = key2 + " "
                charcter.append(key2)
                parent.append(key)
                values.append(value["count"])
                ids.append(key + ' - ' + key2)

    for key, value in count_dict.items():
        for key2, value in count_dict[key]["children"].items():
            for key3, value in count_dict[key]["children"][key2]["children"].items():
                if value["count"] >= MIN_VALUE:
                    charcter.append(key3)
                    parent.append(key + ' - ' + key2)
                    values.append(value["count"])
                    ids.append(key + ' - ' + key2 + ' - ' + key3)

    fig = go.Figure(go.Sunburst(
        labels=charcter,
        parents=parent,
        values=values,
        ids = ids,
        maxdepth=-1,
        insidetextorientation='radial'
    ))

    fig.update_layout(margin = dict(
        # width=500,
        # height=500,
        t=0, l=0, r=0, b=0))

    import plotly.io as pio
    pio.write_image(fig, SUNBURST_PLOT_NAME, width=710, height=700, scale=8)


if __name__ == '__main__':
    main(FILE_NAME, SUNBURST_PLOT_NAME, MIN_VALUE)