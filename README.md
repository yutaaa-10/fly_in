*This project has been created as part of the 42 curriculum by yukurosa.*

# Fly-in

## Description（概要）

Fly-inは、複数のドローンをスタート地点からゴール地点まで効率的に移動させる、経路探索・シミュレーションプロジェクトです。

マップはZone（頂点）とConnection（辺）から構成されるグラフとして表現されます。

単純に最短経路を見つけるだけではなく、ZoneやConnectionの容量、Zoneごとの移動コストなどの制約を考慮し、すべてのドローンがゴールに到着するまでの総ターン数をできるだけ少なくすることを目的としています。
また、Pygameを使用して、ドローンの移動を視覚的に確認できます。

## Instructions（手順）

### 動作環境とインストール

Python 3.10以上と、Pygameのウィンドウを表示できるデスクトップ環境が必要です。
グラフ処理は自作しており、networkxやgraphlibなどのグラフ処理用ライブラリは使用していません。

リポジトリのルートで、仮想環境を作成して依存パッケージをインストールします。

```bash
python3 -m venv .venv
source .venv/bin/activate
make install
```

`make install`は、実行に必要なPygameと、コード検査に使用するflake8・mypyをインストールします。

### コマンドラインから実行

```bash
python3 main.py <map_file>
```

### Makefileから実行

```bash
make run
```

または、マップファイルを指定して実行します。

```bash
make run MAP=maps/medium/01_dead_end_trap.txt
```

`make run`でマップを指定しない場合は、`maps/easy/01_linear_path.txt`を使用します。
コマンドラインからの実行でもMakefileからの実行でも、Pygameのウィンドウが開きます。
起動直後は停止状態です。SpaceまたはEnterキーでシミュレーションを進めてください。

### コード検査と開発用コマンド

```bash
make lint
make lint-strict
make debug MAP=maps/easy/01_linear_path.txt
make clean
```

- `lint`: flake8と、課題指定のオプションを付けたmypyを実行します。
- `lint-strict`: flake8と、strictモードのmypyを実行します。
- `debug`: Pythonのpdbを使って起動します。
- `clean`: Pythonや型検査などのキャッシュを削除します。

### Pygameの操作方法

| キー | 動作 |
|---|---|
| Space | 自動再生を停止し、シミュレーションを1ターン進める |
| Enter | 自動再生・一時停止を切り替える |

自動再生では、0.5秒ごとに1ターン進みます。
すべてのドローンがゴールに到着すると、自動再生が停止します。
終了するには、ウィンドウの閉じるボタンを押してください。

### 実行結果

#### ターミナル出力

各ターンにおけるドローンの移動結果が出力されます。

出力形式は次のとおりです。具体的な入力と対応する出力は、後述の「Example Input and Expected Output」に掲載しています。

- 1ターンを1行とし、そのターンに移動したドローンを空白区切りで出力します。
- 通常の移動と到着は、`D<ID>-<zone>`の形式です。
- restricted Zoneへの移動開始時は、`D<ID>-<connection>`の形式です。接続名には入力で定義した両端のZone名をハイフンでつないだものを使用します。
- restricted Zoneには、移動開始の次のターンに到着し、到着先のZone名を出力します。
- 待機中のドローンと、すでにGoalに到着したドローンは、その後の移動ログには出力しません。
- エラーメッセージは標準エラー出力に表示します。

#### 可視化

Pygameを使用して、Zone、Connection、Droneの状態を描画します。

## 入力データ

マップファイルには、ドローン数、Zone、Connectionなどの情報を記述します。

Zoneは整数座標を持ち、Connectionは双方向の接続を表します。
Zone名にハイフンや空白は使用できません。接続は、その行より前に定義されたZoneを参照します。

| メタデータ | 対象 | 既定値と意味 |
|---|---|---|
| `zone` | Zone | `normal`。移動先Zoneの種類 |
| `color` | Zone | `none`。色情報。現在の描画には反映しません |
| `max_drones` | Zone | `1`。同時に滞在できる機数 |
| `max_link_capacity` | Connection | `1`。同時に通過できる機数 |

StartとGoalのZone容量は無制限で、`max_drones`が指定されていても無視します。

| Zoneの種類 | 移動コスト | 動作 |
|---|---|---|
| `normal` | 1ターン | 通常の移動先 |
| `priority` | 1ターン | 同じ移動コストの経路では優先する |
| `restricted` | 2ターン | 接続上の移動と到着を別ターンで処理する |
| `blocked` | 通行不可 | 経路探索と移動の対象から除外する |

### 入力例

以下のマップを使用した出力は、後述の「Example Input and Expected Output」を参照してください。

```text
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

## プログラム構成

1. コマンドライン引数の取得
2. マップファイルの読み込み
3. Parserによる入力データの解析
4. Graphの構築
5. PathFinderによる経路探索
6. RouterによるDroneの経路割り当て
7. Droneオブジェクトの生成
8. PygameVisualizerのイベントループを開始
9. キー操作や自動再生に応じてSimulatorで1ターン進め、更新後の状態を描画

### 主なクラスと役割

| クラス | 役割 |
|---|---|
| Application | プログラム全体の実行制御 |
| Parser | 入力ファイルの解析・検証 |
| MapData | マップ情報の保持 |
| Graph | グラフの構築 |
| PathFinder | 経路探索 |
| Router | Droneの経路割り当て |
| Drone | Droneの状態管理 |
| Simulator | ドローンの移動シミュレーション |
| PygameVisualizer | Pygameによる可視化 |

## 追加項目（アルゴリズムと実装方針）

### アルゴリズムの詳細

複数のドローンをスタート地点からゴール地点まで効率的に移動させるために、以下の流れで処理を行います。

まず、入力ファイルを解析し、ZoneとConnectionからなるグラフを構築します。
次に、DFS（深さ優先探索）とバックトラッキングを用いて、スタート地点からゴール地点までの複数の経路を探索します。

その後、Routerで各経路のコストを考慮しながらドローンを割り当て、
SimulatorでZoneやConnectionの容量制限を確認しながら、ターンごとにドローンを移動させます。

#### 1. 経路探索（DFS）

Fly-inでは、複数のドローンを効率的に移動させるために、
DFS（深さ優先探索）とバックトラッキングを使用して、
StartからGoalまでのすべてのSimple Path（単純路）を探索します。

##### 探索方法

1. Startから探索を開始します。
2. 現在のZoneに隣接するZoneを取得します。
3. 現在探索中の経路にすでに含まれるZoneと、blocked Zoneを除外します。
4. 現在の経路に含まれないZoneに進み、再帰的に探索を続けます。
5. Goalに到達した場合、現在の経路のコピーを保存します。
6. バックトラッキングによって前のZoneに戻り、別の経路を探索します。

##### 経路の優先順位

探索した経路は、以下の条件で並べ替えます。

1. 移動コストが小さい経路を優先する。
2. 移動コストが同じ場合、priority Zoneを多く含む経路を優先する。

このようにして、DFSで探索した複数の経路を評価し、
Routerによるドローンの経路割り当てに利用します。

#### 2. 経路割り当て（Router）

DFSによって探索した複数の経路に対して、
Routerを使用して、各ドローンを割り当てていきます。
最短経路にすべてのドローンを割り当てると、ZoneやConnectionの容量制限によって、
待機時間が発生する可能性があります。
そこで、経路の移動コストとConnectionの推定混雑度を考慮して、
貪欲法を使用してドローンを1機ずつ割り当てていきます。

##### 混雑度の推定

各Connectionについて、すでに割り当てたドローン数と最大容量から必要な通過グループ数を推定します。
そのConnectionを使用予定のドローンを、容量以下のグループに分けると考え、次の式で計算します。

```text
required_waves = ceil(projected_load / capacity)
```

- projected_load: そのConnectionを使用する予定のドローン数
- capacity: Connectionの最大容量

さらに、移動先のZoneコストを考慮して、Connectionごとの混雑圧力を計算します。

```text
pressure = required_waves * move_cost
```

経路全体の混雑度には、経路内のConnectionのうち、最も大きい混雑圧力を採用します。

```text
congestion = max(Connectionごとのpressure)
score = path_cost + congestion
```

`move_cost`は移動先Zoneのコスト、`path_cost`はStartを除く各移動先Zoneのコストの合計です。
`projected_load`には、すでに割り当てた機数に、今回割り当てる1機を加えます。
このスコアは混雑の目安であり、実際の到着ターン数を厳密に計算するものではありません。
Zone容量はRouterのスコアには直接含めず、Simulatorで移動の可否を判定します。

##### ドローンの割り当て

1. 各経路のスコアを計算します。
2. 最もスコアが小さい経路を選択します。
3. その経路にドローンを1機割り当てます。
4. 選択した経路のConnectionの負荷を更新します。
5. すべてのドローンを割り当てるまで繰り返します。

このように、経路コストだけでなく、
Connectionの混雑も考慮してドローンを分散させることで、
全体の到着ターン数の短縮を目指します。
なお、この方法は貪欲法による近似的な割り当てであり、
必ずしも全体の最適解を保証するものではありません。

##### 貪欲法

貪欲法とは、各ステップにおいて、その時点で最も良いと判断できる選択を繰り返すアルゴリズムです。
本プロジェクトでは、ドローンを1機ずつ割り当てる際に、各経路のコストと、推定混雑度からスコアを計算して、
最もスコアの小さい経路を選択します。
ドローンを割り当てた後は、その経路で使用するConnectionの負荷を更新し、次のドローンの経路選択に反映させます。
この処理をすべてのドローンに対して、繰り返すことで、特定の経路への集中を抑えて、複数の経路にドローンを分散させます。
ただし、貪欲法は各ステップでの最善の選択を繰り返すため、全体としての最適解が必ず得られるとは限りません。

##### 計算量と制約

経路探索とコスト計算はシミュレーション開始前に実行し、各ターンで経路を再探索しません。
ただし、すべての単純路を列挙するため、密なグラフでは候補数が急増し、探索時間とメモリ使用量が大きくなります。
通常のDFSの`O(V + E)`は、この全単純路列挙の計算量には当てはまりません。

候補経路数を`P`、最大経路長を`L`、ドローン数を`D`とすると、経路保存には`O(P × L)`のメモリを使用します。
Routerの割り当て処理は、おおむね`O(D × P × L)`です。
全体の最適解や、すべてのマップでの目標ターン数の達成は保証しません。

#### 3. 移動シミュレーション（Simulator）

Routerによって各ドローンの経路を決定したあと、
Simulatorでターン単位の移動処理を実行します。
Simulatorでは、ZoneとConnectionの容量制限を考慮しながら、
各ドローンを割り当てられた経路に沿って移動させます。

##### 1ターンの処理

1. ターン数を更新し、Zoneの占有数、Connectionの使用数、Zoneの予約数を取得します。
2. 移動中のドローンを処理し、到着した場合はZoneの占有数を更新します。
3. ドローンを経路上の進行状況に応じて並べ替えます。
4. 各ドローンについて、次のZoneへの移動が可能か判定します。
5. 移動可能な場合はドローンの状態を更新し、移動できない場合は待機させます。
6. そのターンの移動結果を出力します。

##### Restricted Zoneの処理

Restricted Zoneへの移動には追加のターンが必要です。
通常のZoneでは1ターンで移動が完了しますが、
Restricted Zoneでは合計2ターンを使い、移動開始の次のターンに必ず到着します。
接続上で追加の待機は行いません。
移動中のドローンはZoneの占有数から除外し、
Connectionの使用数と到着先Zoneの予約数によって管理します。

##### 終了判定

すべてのドローンがGoalに到着すると、移動処理が完了し、自動再生を停止します。
描画用ウィンドウは、閉じる操作を行うまで表示を続けます。
また、未到着のドローンが存在するにもかかわらず、
1ターンの間に移動の開始・完了が発生しなかった場合は、
デッドロックとしてエラーを出力します。

### 視覚表現

Pygameを使用してマップとドローンの移動を可視化しました。
ZoneとConnectionで構成されるグラフを画面上に描画し、
各ターンにおけるドローンの位置を視覚的に確認できます。
ターミナルの出力だけでは把握しにくいドローンの移動経路や待機状況を、
直感的に理解できるようにすることを目的としています。

#### マップの可視化

Zoneを円、Connectionを線として描画し、各Zoneの名前を表示します。
また、Zoneの種類に応じて色分けしています。

| Zoneの種類 | 色 |
|---|---|
| Normal / Priority | 青 |
| Restricted | オレンジ |
| Blocked | グレー |

これにより、マップの接続関係や、Restricted・Blocked Zoneの位置を視覚的に把握できます。

現在の実装では、StartとGoalは通常のZoneと同じ型別の配色で表示されます。
入力の`color`メタデータは保持しますが、描画色には反映していません。
課題で指定された色情報の視覚的な反映については、実装側に対応が残っています。
StartとGoalを専用色で区別する表示も、今後の改善候補です。

#### ドローンの可視化

ドローンは黄色い小さな円として描画します。
同じZoneに複数のドローンが存在する場合は、
三角関数（sin、cos）を使用して円周上に均等に配置します。
これにより、ドローン同士の重なりを減らし、
各Zoneに存在するドローンの数を確認しやすくしています。

現在の描画では、restricted Zoneへの移動中のドローンも出発元のZoneに表示します。
接続上の位置は描画しないため、移動中かどうかはターミナルの接続名の出力で確認します。
Goalに到着したドローンは移動処理の対象から外れますが、描画上はGoalに表示を続けます。

#### 座標の自動調整

入力ファイルに記述されたZoneの座標を、
Pygameの画面座標に変換して描画します。
マップ全体の座標範囲から中心位置と拡大率を計算し、
ウィンドウ内にマップが収まるように自動調整します。
これにより、異なる座標範囲のマップでも、
手動で描画位置を調整することなく表示できます。

#### シミュレーション操作

キーボード操作によって、シミュレーションの進行を制御できます。

| キー | 操作 |
|---|---|
| Space | 1ターン進める |
| Enter | 自動再生・一時停止 |

自動再生では、0.5秒ごとに1ターン進みます。
手動操作では、ドローンの移動や待機を1ターンずつ確認でき、
自動再生ではシミュレーション全体の流れを確認できます。

すべてのドローンがGoalに到着すると、自動再生は停止します。

#### Simulatorとの連携

Simulatorがドローンの移動状態を更新し、
PygameVisualizerがその状態を描画する構成にしています。

シミュレーション処理と描画処理の責務を分離することで、
移動ロジックを変更せずに表示方法を改善できる設計にしています。

## Example Input and Expected Output

### 入力例

`maps/medium/01_dead_end_trap.txt`

```text
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

### 実行方法

```bash
python3 main.py maps/medium/01_dead_end_trap.txt
```

### 出力例

Spaceキーで進めるか、Enterキーで自動再生を開始すると、Simulatorが各ターンの移動結果を標準出力に表示します。
この入力では、現在の実装で全5機が8ターンで到着します。

```text
D1-junction D2-junction
D1-correct_path D3-junction
D1-intermediate D2-correct_path D4-junction
D1-goal D2-intermediate D3-correct_path D5-junction
D2-goal D3-intermediate D4-correct_path
D3-goal D4-intermediate D5-correct_path
D4-goal D5-intermediate
D5-goal
```

また、Pygameのウィンドウでは、マップとドローンの位置を視覚的に確認できます。
Spaceキーで1ターンずつ進めることができ、Enterキーで自動再生・一時停止を切り替えられます。

## Resources

本プロジェクトの実装にあたり、以下の資料を参考にしました。

### コマンドライン引数の解析

- [ArgumentParserの使い方を簡単にまとめた](https://qiita.com/kzkadc/items/e4fc7bc9c003de1eb6d0)
- [argparse --- コマンドラインオプションや引数、サブコマンド向けのパーサー](https://docs.python.org/ja/3/library/argparse.html)

### アルゴリズム

- [Pythonオンライン学習サービス PyQ（パイキュー）ドキュメント](https://docs.pyq.jp/python/math_opt/graph)
- [深さ優先探索と幅優先探索の理論を学び Python で実践](https://zero2one.jp/learningblog/breadth-first-depth-first-search/?srsltid=AU7gw4UmsaIwrzV8fixIU20hT-osCfaz6tZBSUozQiHoeyNk8h4p-Akn)
- [貪欲法とは？ Pythonによるコード例](https://tech.aru-zakki.com/greedy-algolithm/)
- [Pythonで始める最適化入門──AI活用から「意思決定」の道筋まで見つける方法とは？](https://techplay.jp/column/1576)
- [heapq — Heap queue algorithm](https://docs.python.org/3/library/heapq.html)

### 視覚化

- [Pythonでゲーム開発！pygameとは？入門からゲームサンプルまで](https://qiita.com/nagamie/items/0f7f3e2ea029855a16a1)
- [Pygameで使える関数・メソッド・クラス一覧まとめ](https://programming-mondai.com/top/pygame/yougo/)
- [pygame.key](https://www.pygame.org/docs/ref/key.html)

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
アルゴリズムやコードの意味の確認に利用しました。
READMEの構成確認、課題要件との照合、記述と実装の整合性確認、文章の校閲・修正にもAIを使用しました。
