# cloudio
PythonでWebやAWS S3上のファイルをローカルにあるかのように入出力できるようになる。



## Features

-   [x] 通常のopenのようなインターフェースでHttps / S3 のファイルをreadする
-   [x] 通常のopenのようなインターフェースでS3へファイルをwriteする
-   [x] pandasなどのライブラリでも簡単にクラウドのファイルを読めるようにできる
-   [x] 通常のopenとの互換性があり、既存コードからの移行が簡単
-   [x] easy to install
-   [x] (AllenNLPのcached_pathのみをpip installできる)
-   [x] default encoding utf-8



## Usage

```shell
$ pip install git+https://github.com/elyza-inc/cloudio.git

# S3を使いたいがAWS cliの設定が出来ていない場合は以下のように設定
$ pip install awscli
$ awscli configure
# 管理者に発行してもらったアクセストークンを登録する
```



```Python
from cloudio import copen

# クラウド・Web上のデータを読み込み (ダウンロード)
with copen('https://example.com/hoge.txt', 'r') as f:
  text = f.read()

# クラウドに書き込み (アップロード)
with copen('s3://elyza-bucket/fuga.txt', 'w') as f:
  f.write(text)


# file-like objectなのでpandasなどのライブラリもクラウド上のデータが使えるようになる
with copen('s3://elyza-bucket/data.csv', 'r') as f:
  df = pd.read_csv(f)
  

# 通常のopenとも互換性があるので、ローカルファイルの読み書きもできる
with copen('/home/local/file', 'r') as f:
  text = f.read()
```



### 複数のAWSプロファイルを使い分けているとき

copenを使用する前に使用プロファイルの設定を行う

```python
import cloudio
cloudio.set_config(s3_profile='profile_name')
```



#### cached_path

```python
from cloudio import cached_path
path = cached_path('https://example.com/hoge.txt')
# ローカルのキャッシュへのパスが返される
```



## Limitations & TODO

* S3以外 (Google cloud storage など) には対応していない
* シングルファイルの入出力のみ
* zipとかでディレクトリごとダウンロードなどはまだできない
* 圧縮せずにダウンロード&アップロードするので通信が遅くなる
* ネットに上がっているデータは圧縮されていることも多いので、それをそのまま使えるようにしたい



## 内部動作

*   read
    *   初回はs3からダウンロードしてローカルにキャッシュした上で、そのキャッシュしたファイルを読む
*   write
    *   tmpファイルに書き込み、with句から抜けるタイミングでアップロード