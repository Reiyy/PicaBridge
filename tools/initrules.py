import json
import os
from datetime import datetime

def load_tags(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_rules(rules, file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    else:
        existing_data = {"tags": {}, "author": {}, "info": {"date": ""}}
    
    existing_data["tags"].update(rules["tags"])
    existing_data["author"].update(rules["author"])
    existing_data["info"]["date"] = datetime.now().strftime("%Y%m%d")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=4)

def create_rules(tags_data, namespace_name=None):
    tags = {}
    author = {}

    for entry in tags_data["data"]:
        entry_name = entry["frontMatters"]["name"]
        # 处理author组，去除标签命名空间减少占地面积
        if entry_name in ["团队", "艺术家", "Coser"]:
            for tag_key, tag_info in entry["data"].items():
                author[f"{entry_name}:{tag_info['name']}"] = tag_info['name']
        
        # 处理tags组，排除项目
        if namespace_name is None or entry_name == namespace_name:
            for tag_key, tag_info in entry["data"].items():
                tag_name = tag_info["name"]
                
                # 对男性和女性进行特殊处理，只去掉右边的“性”字
                if entry_name == "男性":
                    tags[f"{entry_name}:{tag_name}"] = f"男:{tag_name}"  # 替换值
                elif entry_name == "女性":
                    tags[f"{entry_name}:{tag_name}"] = f"女:{tag_name}"  # 替换值
                else:
                    if entry_name not in ["团队", "艺术家", "Coser", "重新分类"]:
                        if not (entry_name == "语言" and tag_name in ["汉语", "日语", "英语"]):
                            tags[f"{entry_name}:{tag_name}"] = f"{entry_name}:{tag_name}"

    return {"tags": tags, "author": author}

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    db_file = os.path.join(root_dir, 'db.text.json')
    rules_file = os.path.join(root_dir, 'arules.json')
    
    tags_data = load_tags(db_file)
    
    print("请选择操作:")
    print("1. 指定类型")
    print("2. 全部类型")
    choice = input("请输入选项（1/2）：")
    
    if choice == '1':
        namespace_name = input("请输入要创建的类型名称：")
        rules = create_rules(tags_data, namespace_name)
    elif choice == '2':
        rules = create_rules(tags_data)
    else:
        print("无效选项，请重新选择。")
        return
    
    print(json.dumps(rules, ensure_ascii=False, indent=4))
    print(f"总共 {len(rules['tags'])} 个标签，{len(rules['author'])} 个作者。")
    
    save_rules(rules, rules_file)

if __name__ == '__main__':
    main()
