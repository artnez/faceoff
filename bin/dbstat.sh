#! /usr/bin/env bash
db_path=${1:-"$HOME/.faceoff.tmp.db"}
if [ ! -f $db_path ]; then
    echo "db file not found: ${db_path}"
    exit 1
fi

query() {
    result=$(sqlite3 "$db_path" "$1" 2> /dev/null) 
    echo "$result" | grep -Ev '\-\- Loading resources from'
    echo ""
}

query "select tbl_name from sqlite_master where type='table';" 
query "select * from setting;"
query "select * from user;"
query "select id, slug, name, active, date_created from league;"
query "select * from match;"
query "select * from ranking;"
