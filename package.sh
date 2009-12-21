#!/bin/sh
name="ts3query-$1"
svn export . "$name"

cd "$name" && tar xvzf ../web/web.py-0.33.tar.gz web.py-0.33/web/
mv web.py-0.33/web . && rmdir web.py-0.33
rm package.sh
cd ..

tar cvjf packages/"$name".tar.bz2 "$name"
zip -r packages/"$name".zip "$name"
rm -rI "$name"
