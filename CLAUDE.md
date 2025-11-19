# 若要 checkout @config/widget 裡面的檔案

如果

1. 改動的檔案是 `type: custom-api` 且是 yml 檔

2. 同一層資料夾有 README.md，且是該 yml 檔案的說明文件

必須在 checkout 之前把同一層的 `README.md` 說明文件一併更新該次的修改

# 若指令是「檢查 css」，則需要檢查檔案是否符合以下規則:

1. glance dashboard 共用的 class `https://g1ance.zeabur.app/static/02b8858d2d/css/bundle.css` (並且不能用定義給 custom-api widget 的 class)

2. 自定義的 class (若是自定義的 custom-api widget 的 class 格式必須是 `.{class}-{widget-name}` )

若不符合以上規則，則需要調整至符合上述規則

> 補充：
> Don't rely on the CSS classes that are specific to existing widgets:
> `<img class="twitch-category-thumbnail" src="...">`
> Instead, embed the necessary CSS directly:
> `<img style="width: 5rem; aspect-ratio: 3 / 4; border-radius: var(--border-radius);" src="...">`
> This reduces the odds of your widget breaking in the future if the CSS classes get modified. You can use all the utility classes such as flex, color-primary, size-h3, text-center, etc, as those are unlikely to change.

# 若是在開發 custom-api (widget)，裡面的 template 必須先閱讀下方 template 文件，以確保語法正確

文件：https://raw.githubusercontent.com/glanceapp/glance/refs/heads/main/docs/custom-api.md

# Glance Custom-API Widget Template 開發筆記

## 問題：GJSON Array 元素的字串格式化陷阱

### 場景

在 Glance 的 `custom-api` widget 中撰寫 template 時，需要比對來自不同 API
或不同路徑的 ID 值。

### 技術背景

Glance 使用 **GJSON** 庫解析 API 返回的 JSON 數據。GJSON 的不同取值方法
返回不同的類型，這些類型在使用 `printf "%v"` 格式化時會產生不同的字串表示。

### 核心問題

當使用 `.Array` 方法獲取 JSON 陣列時，陣列中的每個元素都是
`glance.decoratedGJSONResult` 類型。這個類型在格式化為字串時會**自動添加
大括號 `{}`**。

#### 實際案例：Raindrop API

```yaml
# API 1: GET /user
{
  "user": {
    "groups": [
      {
        "title": "收藏夾",
        "collections": [63388829, 63388989, 63389172]  # JSON 中是純數字陣列
      }
    ]
  }
}

# API 2: GET /collections
{
  "items": [
    {"_id": 63388829, "title": "Quick Link"},      # JSON 中是純數字
    {"_id": 63388989, "title": "Entertainment"}
  ]
}

Template 中的問題

# 從 user API 獲取 collection IDs
{{ $groupCollectionIds := .JSON.Array "user.groups.0.collections" }}

# 從 collections API 獲取 collection 物件
{{ $allCollections := .JSON.Array "items" }}

# 嘗試比對
{{ range $collId := $groupCollectionIds }}
  {{ range $allCollections }}
    # ❌ 這樣比對會失敗！
    {{ if eq (printf "%v" $collId) (printf "%v" (.Int "_id")) }}
      # $collId 會是 "{63388829}"  ← 有大括號
      # .Int "_id" 會是 "63388829"  ← 沒有大括號
      # 永遠不會匹配！
    {{ end }}
  {{ end }}
{{ end }}

型別差異對照表

| 來源方法              | Go 類型                       | printf "%v" 輸出 | 原因                              |
|-------------------|-----------------------------|----------------|---------------------------------|
| .Array "path" 的元素 | glance.decoratedGJSONResult | {63388829}     | GJSON Result 的 String() 方法添加大括號 |
| .Int "path"       | int64                       | 63388829       | Go 原生整數直接格式化                    |
| .String "path"    | string                      | hello          | Go 原生字串直接格式化                    |

解決方案

✅ 方法：使用 trimPrefix/trimSuffix 去除大括號

{{ range $collId := $groupCollectionIds }}
  # 1. 格式化為字串
  {{ $collIdStr := printf "%v" $collId }}

  # 2. 移除 GJSON Result 添加的大括號
  {{ $collIdStr = trimPrefix "{" $collIdStr }}
  {{ $collIdStr = trimSuffix "}" $collIdStr }}

  # 3. 現在可以正確比對
  {{ range $allCollections }}
    {{ if eq $collIdStr (printf "%v" (.Int "_id")) }}
      # ✓ 匹配成功！
    {{ end }}
  {{ end }}
{{ end }}

判斷規則

在 Glance custom-api template 中：

1. 使用 .Array 取得的陣列元素
  - ⚠️ 需要去除大括號才能比對
  - 適用：user.groups, items, 任何陣列的元素
2. 使用 .Int/.String/.Bool 直接取值
  - ✓ 不需要特殊處理
  - 適用：._id, .title, .count 等物件屬性
3. Debug 技巧
# 檢查變數類型
Type: {{ printf "%T" $var }}

# 檢查格式化結果
Value: {{ printf "%v" $var }}

實際應用位置

- config/widget/raindrop-bookmarks/raindrop-bookmarks.yml:127-130
- 任何需要比對來自 .Array 的元素與其他值的場景
```

