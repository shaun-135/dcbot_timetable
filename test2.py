import os
from matplotlib import pyplot as plt
from matplotlib import font_manager

# 獲取根目錄路徑並構建字體文件的完整路徑
font_path = os.path.join(os.getcwd(), '/workspaces/dc-----/msjh.ttf')  # 假設你的 ttf 文件名為 'msjh.ttf'

# 確認字體文件路徑是否正確
if not os.path.isfile(font_path):
    raise FileNotFoundError(f"字體文件未找到: {font_path}")

# 設置字體屬性
font_prop = font_manager.FontProperties(fname=font_path)

# 配置 matplotlib 使用該字體
plt.rcParams["font.sans-serif"] =  [font_prop.get_name()]  # 設置默認字體
plt.rcParams["axes.unicode_minus"] = False  # 避免負號顯示問題

# 測試：生成一個圖，並在圖中顯示中文
plt.figure()
plt.text(0.5, 0.5, "測試文字", ha='center', va='center', fontsize=15, fontproperties=font_prop)
plt.show()

# 保存圖表
output_path = os.path.join(os.getcwd(), 'output_image.png')  # 這會把圖片儲存到根目錄
plt.savefig(output_path)

# 關閉圖片
plt.close()
