import json


def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# 提取作者信息
def extract_author(tags_str):
    for tag in tags_str.split(","):
        if tag.startswith("artist:"):
            return tag.split(":", 1)[1]
        elif tag.startswith("艺术家:"):
            return tag.split(":", 1)[1]
    return ""

# 分类匹配
def match_categories(tags_str, pagecount):
    config = load_config()
    categories_config = config.get("categories", {})
    categories = ["短篇"] if pagecount < 95 else ["长篇"]

    for category, data in categories_config.items():
        rule = data.get("rule", []) if isinstance(data, dict) else data

        if not rule:
            continue

        match_mode = rule[0]
        match_tags = rule[1:]

        if match_mode == 1 and all(tag in tags_str for tag in match_tags):
            categories.append(category)
        elif match_mode == 0 and any(tag in tags_str for tag in match_tags):
            categories.append(category)

    return list(set(categories))

# 标签简化
def clean_tags(tags_str):
    cleaned_tags = []
    for tag in tags_str.split(","):
        if tag.startswith(("source:", "date_added:", "艺术家:", "artist:", "上传者:", "时间戳:",
                           "group:", "language:", "语言:汉语", "语言:翻译", "uploader:", "timestamp:")):
            continue
        elif tag.startswith("男性:"):
            cleaned_tags.append("男:" + tag[3:])
        elif tag.startswith("女性:"):
            cleaned_tags.append("女:" + tag[3:])
        else:
            cleaned_tags.append(tag)
    return cleaned_tags

# 时间戳提取
def extract_timestamp(tags_str):
    for tag in tags_str.split(","):
        if tag.startswith("date_added:"):
            return int(tag.split(":", 1)[1])
    return None
