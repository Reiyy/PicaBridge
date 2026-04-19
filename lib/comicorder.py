import json

import lib.api as api

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()
LRR_URL = config.get('lrr_Api')
PICABRIDGE_URL = config.get('PicaBridge_URL')

# 获取档案页数
def get_pages(comic_id, page, order):
    # 从 API 获取档案数据
    extract_data = api.get_extract_archive(comic_id)
    if not extract_data:
        return {"code": 404, "message": "Extract archive not found"}
    
    pages_list = extract_data.get("pages", [])

    # 获取 metadata
    metadata = api.get_archive_metadata(comic_id)
    if not metadata or "pagecount" not in metadata:
        return {"code": 404, "message": "Comic metadata not found"}

    total_pages = metadata["pagecount"] # 所有图片总页数
    toc = metadata.get("toc", []) # 章节列表

    # 如果存在章节数据，处理章节分页
    if toc:
        # 将从1开始的order章节号转换成从0开始的json列表号
        index = order - 1

        # 避免order为0或大于总章节数
        if index < 0 or index >= len(toc):
            return {"code": 400, "message": "Invalid order"}

        # 从toc数据获取当前请求章节起始页
        start_page = toc[index].get("page", 1)

        # 获取下一个章节起始页并减一作为当前章节结束页，如果没有下一个章节，用总页数作为结束页
        if index + 1 < len(toc):
            end_page = toc[index + 1].get("page", total_pages + 1) - 1
        else:
            end_page = total_pages

        # 计算当前章节图片的起始和结束索引
        start_index = max(start_page - 1, 0)
        end_index = min(end_page, len(pages_list))
        # 当前章节的图片列表
        chapter_pages = list(enumerate(pages_list[start_index:end_index],start=start_index))
        # 获取章节标题
        ep_title = toc[index].get("name", f"Chapter {order}")

    else:
        # 无章节数据的情况下返回所有图片列表
        chapter_pages = list(enumerate(pages_list,start=0))
        ep_title = extract_data.get("title", "第一话")

    # 分页
    total = len(chapter_pages)
    limit = 40 # 每页的限制数量
    pages = (total + limit - 1) // limit if total > 0 else 1

    # 验证请求的页码是否在有效范围内
    if page < 1 or page > pages:
        return {"code": 400, "message": "Invalid page number"}

    # 计算当前页的起始和结束索引
    start = (page - 1) * limit
    end = min(start + limit, total)

    # 按照分页获取图片 URL
    paginated_pages = chapter_pages[start:end]

    # 构建返回的 docs 数据
    docs = []
    # 使用全局页码避免使用章节内页码造成页码重复
    for global_index, page_url in paginated_pages:
        global_index = global_index + 1  # 转成从1开始的页码
        original_name = page_url.split("/")[-1] # 获取原始文件名
        doc_id = f"{comic_id[:20]}{global_index:04d}" # 根据 comic_id 和页数生成 ID
        media = {
            "originalName": original_name,
            "path": "lrr_img" + page_url,
            "fileServer": PICABRIDGE_URL
        }
        docs.append({
            "_id": doc_id,
            "media": media,
            "id": doc_id
        })

    # 返回
    response_data = {
        "code": 200,
        "message": "success",
        "data": {
            "pages": {
                "docs": docs,
                "total": total,
                "limit": limit,
                "page": page,
                "pages": pages
            },
            "ep": {
                "_id": comic_id,
                "title": ep_title
            }
        }
    }
    
    return response_data