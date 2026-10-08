*This project has been created as part of the 42 curriculum by yukurosa.*


# Fly-in


## 概要
Fly_inは、複数のドローンをスタート地点からゴール地点まで移動させる、
経路探索、趣味レーションプロジェクトです。

マップはZoneとConnectionによるグラフとして表現されます。

単純に最短経路を見つけるだけではなく、
ZoneやConnectionの容量、Zoneごとの移動コストなどの制約を守りながら、
全てのドローンがゴールに到着するまでの総ターンを数を
できるだけ少なくすることが目的です。


## 手順

###　　実行方法

```
python3 main.py <map_file>
```

### 実行結果

```

```

### 入力データ
例
```
nb_drones: 5

start_hub: start 0 0 [color=green]
hub: junction 1 0 [color=yellow max_drones=2]
hub: dead_end 1 1 [color=red]
hub: correct_path 2 0 [color=blue]
hub: intermediate 3 0 [color=blue]
end_hub: goal 4 0 [color=green]

connection: start-junction [max_link_capacity=2]
connection: junction-dead_end
connection: junction-correct_path
connection: correct_path-intermediate
connection: intermediate-goal
```
入力ファイルには主に以下の情報が含まれます。

* ドローン数
* スタート地点
* ゴール地点
* Zone
* Connection
* Zoneの種類
* Zoneの最大ドローン数
* Connectionの最大容量

Zoneには以下の種類があります。

* normal: 移動コスト1
* priority: 移動コスト1、優先的に使用する
* restricted: 移動コスト2
* blocked: 通行不可

### プログラム構成

1. コマンドライン引数の取得
2. ファイルの読み込み
3. Parserの実行
4. Graphの構築
5. 経路探索
6. シミュレーション


##　追加項目

###　使用したアルゴリズム

#### BFS
最初に、重みを考えない最短経路探索として、BFSを実装しました。
BFSではqueueを使用し、スタート地点から近いZoneを順に探索します。
そのため、通過するConnectionの数が少ない経路を求めることができます。
しかし、Zoneによってコストが異なるため、BFSだけでは不十分です。

### Dijkstra
Zoneの移動コストを考慮するために、Dikstra法を実装しました。
BFSがqueueに入った順番で探索するのに対して、Dijkstraではスタート地点からの累積コストが、
最も小さいZoneを次に探索します。
Priority Queueを使用して、現時点で最も小さい累積コストを持つZoneを取り出します。
すでに発見したZoneに対して、より小さいコストで到達できる経路を発見した場合は、
その最短距離を更新します。

#### DFS
複数のドローンを扱う場合、全ドローンを一本の経路に流すことが最適とは限りません。
ZoneやConnectionには容量制限があるため、複数の経路にドローンを分散した方が、
全体の到着時間を位自覚できる可能性があります。
そこでDFSとバックトラッキングを使用して、
startからgoalまでの複数のsimple pathを探索します。


###　 視覚表現


### 入力例と期待される出力


## Resources
最終提出までに、実際に参考にした資料を記載します。

* Python公式ドキュメント
* argparse
* collections.deque
* heapq
* BFS
* DFS
* Dijkstra
* Graph theory


### AIの使用について

AIは主に学習・設計を補助する目的で使用しました。

主な用途：

* グラフ理論の理解
* BFS / DFS / Dijkstraの理解
* OOP設計の整理
* ParserのValidation設計
* エラーやバグの原因調査
* Python標準ライブラリの理解

AIの出力をそのまま使用するのではなく、
アルゴリズムやコードの意味の確認に利用。
