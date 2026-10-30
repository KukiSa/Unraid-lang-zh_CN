#!/bin/bash
# Offline install through Unraid's native language manager. GPL-2.0-only.
set -euo pipefail

bundle_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
manager=/usr/local/emhttp/plugins/dynamix.plugin.manager/scripts/language
boot_plugins=/boot/config/plugins
state_dir="$boot_plugins/unraid-zh-cn-independent"
target_zip="$boot_plugins/dynamix/lang-zh_CN.zip"

if [[ $(id -u) != 0 || ! -f /etc/unraid-version || ! -x "$manager" ]]; then
  printf '%s\n' '请在 Unraid 服务器的终端中，以 root 用户运行此脚本。' >&2
  exit 1
fi
for command in sha256sum unzip tar; do
  command -v "$command" >/dev/null || { printf '缺少命令：%s\n' "$command" >&2; exit 1; }
done
(cd "$bundle_dir" && sha256sum --check SHA256SUMS)
unzip -tqq "$bundle_dir/zh_CN.zip"

backup_dir="$state_dir/backups/$(date -u +%Y%m%dT%H%M%SZ)-$$"
mkdir -p "$backup_dir" "$boot_plugins/dynamix"
for item in boot_xml boot_zip runtime_xml pending_xml; do
  case "$item" in
    boot_xml) old_file="$boot_plugins/lang-zh_CN.xml" ;;
    boot_zip) old_file="$target_zip" ;;
    runtime_xml) old_file=/var/log/plugins/lang-zh_CN.xml ;;
    pending_xml) old_file=/tmp/plugins/lang-zh_CN.xml ;;
  esac
  if [[ -f "$old_file" ]]; then cp -- "$old_file" "$backup_dir/$item"; fi
done
if [[ -d /usr/local/emhttp/languages/zh_CN ]]; then
  tar -C /usr/local/emhttp/languages -cf "$backup_dir/live.tar" zh_CN
fi
printf '%s\n' 'unraid-zh-cn-independent-backup-v1' > "$backup_dir/format"
cp -- "$bundle_dir/restore-language.sh" "$backup_dir/restore-language.sh"

cp -- "$bundle_dir/zh_CN.zip" "$target_zip.new"
mv -- "$target_zip.new" "$target_zip"
# Remove a previously downloaded update descriptor for the official Chinese pack.
rm -f -- /tmp/plugins/lang-zh_CN.xml
if ! "$manager" install "$bundle_dir/lang-zh_CN.xml"; then
  printf '%s\n' '安装失败，正在恢复原语言包。' >&2
  bash "$backup_dir/restore-language.sh" "$backup_dir"
  exit 1
fi
printf '\n%s\n' '安装完成。前往 Settings → Display Settings → Language，选择中文并应用。'
printf '原语言包备份：%s\n' "$backup_dir"
printf '恢复命令：bash "%s/restore-language.sh" "%s"\n' "$backup_dir" "$backup_dir"
