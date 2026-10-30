#!/bin/bash
# Restore exactly the language artifacts saved by install-offline.sh.
set -euo pipefail
backup_dir="${1:-}"
if [[ $(id -u) != 0 || ! -f /etc/unraid-version ]]; then
  printf '%s\n' '请在 Unraid 服务器上以 root 用户运行此脚本。' >&2
  exit 1
fi
case "$backup_dir" in
  /boot/config/plugins/unraid-zh-cn-independent/backups/*) ;;
  *) printf '%s\n' '请提供安装时输出的原语言包备份目录。' >&2; exit 1 ;;
esac
[[ -f "$backup_dir/format" ]] && [[ $(cat "$backup_dir/format") == unraid-zh-cn-independent-backup-v1 ]] || {
  printf '%s\n' '不是有效的语言包备份目录。' >&2; exit 1;
}
boot_plugins=/boot/config/plugins
if [[ -f "$backup_dir/live.tar" ]]; then
  tar -tf "$backup_dir/live.tar" >/dev/null
fi
mkdir -p "$boot_plugins/dynamix" /var/log/plugins /tmp/plugins /usr/local/emhttp/languages
for item in boot_xml boot_zip runtime_xml pending_xml; do
  case "$item" in
    boot_xml) target="$boot_plugins/lang-zh_CN.xml" ;;
    boot_zip) target="$boot_plugins/dynamix/lang-zh_CN.zip" ;;
    runtime_xml) target=/var/log/plugins/lang-zh_CN.xml ;;
    pending_xml) target=/tmp/plugins/lang-zh_CN.xml ;;
  esac
  rm -f -- "$target"
  if [[ -f "$backup_dir/$item" ]]; then cp -- "$backup_dir/$item" "$target"; fi
done
rm -rf -- /usr/local/emhttp/languages/zh_CN
if [[ -f "$backup_dir/live.tar" ]]; then
  tar -C /usr/local/emhttp/languages -xf "$backup_dir/live.tar"
fi
if [[ -f "$backup_dir/boot_xml" && -f "$backup_dir/runtime_xml" ]]; then
  rm -f -- /var/log/plugins/lang-zh_CN.xml
  ln -s "$boot_plugins/lang-zh_CN.xml" /var/log/plugins/lang-zh_CN.xml
fi
rm -f -- /usr/local/emhttp/webGui/javascript/translate.zh_CN.js
printf '%s\n' '原语言包已恢复。请刷新页面，必要时在显示设置中重新选择语言。'
