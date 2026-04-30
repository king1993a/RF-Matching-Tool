RF-Matching-Tool (RF 阻抗匹配自動化與視覺化工具)
這是一個基於 Python 開發的射頻阻抗匹配工具，旨在自動化計算 L-Match 匹配網路參數，並提供直觀的史密斯圖 (Smith Chart) 軌跡視覺化。本工具特別適用於高頻電路設計前期，快速評估元件數值與匹配路徑。
核心功能 (Core Features)自動化匹配計算：支援複數源阻抗 ($Z_S$) 與負載阻抗 ($Z_L$) 的共軛匹配計算。
拓樸自動切換：根據負載在史密斯圖上的位置，自動判斷並切換 L-Match 拓樸（如 Shunt-Series 或 Series-Shunt），以確保路徑避開匹配禁區。
路徑視覺化：整合 matplotlib 與 scikit-rf，動態繪製阻抗移動軌跡（恆定電阻/電導圓弧線）。
元件數值轉換：自動根據操作頻率（如 2.4 GHz 或 28 GHz）將電抗值轉換為實體 SMD 元件數值（nH/pF）。
技術堆疊 (Tech Stack)
Python 3.xNumpy: 處理複數阻抗矩陣運算。
Matplotlib: 負責繪製高品質的史密斯圖與軌跡曲線。
scikit-rf (skrf): 提供標準的射頻工程計算與座標轉換。
實作原理 (Implementation Logic)本工具透過解析幾何方式模擬元件在史密斯圖上的移動：
並聯電容/電感：阻抗沿著恆定電導圓 (Constant Admittance Circle) 移動。
串聯電容/電感：阻抗沿著恆定電阻圓 (Constant Resistance Circle) 移動。
程式會自動迭代尋找這兩條圓弧的交點，從而得出精確的元件數值。
