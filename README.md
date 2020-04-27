# cloudio
PythonでWeb上のファイルやAWS S3, Google cloud storageをローカルにあるかのように扱えるようにする。


## 方針
* とりあえずAllenNLPのcached_pathだけをインストールできるようにする
* その後、こんな感じでioを既存のものから移行できるようにできたら嬉しい

```Python

import cloudio as cio

cio.set_config(s3_profile='elyza')

with cio.open('s3://elyza-bucket/hoge', 'r') as f:
  # 初回はs3からダウンロードしてローカルにキャッシュした上で、そのキャッシュしたファイルを読む
  contents = f.read()

with cio.open('s3://elyza-bucket2/fuga', 'w') as f:
  # tempファイルに書き込み、__exit__のタイミングでファイルをアップロードする
  f.write(contents)


# file-like objectなので多分こういうふうにもかける
with cio.open('s3://elyza-bucket/data.csv', 'r') as f:
  # 初回はs3からダウンロードしてローカルにキャッシュした上で、そのキャッシュしたファイルを読む
  df = pd.read_csv(f)
```

* zipとかでディレクトリごとダウンロード的なやつは未定。一回解凍してディレクトリ毎S3においておけばとりあえず対応できるが...
* あとデフォルトのエンコーディングはutf-8にするなど

## c.f.
* cloudio
  * https://cloudstorage.readthedocs.io/en/latest/installation.html