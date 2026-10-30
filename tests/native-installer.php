<?php
// Copyright 2005-2023, Lime Technology
// Copyright 2012-2023, Bergware International. GPL-2.0-only.
// Source: unraid/webgui 975475904af36845053e3f96bd7a84f85fd2a969
// Official language manager functions, unraid/webgui, GPL-2.0-only.
function valid_language_pack_name($name): bool {
  return is_string($name) && $name !== '' && preg_match('/^[A-Za-z0-9._$-]+$/', $name);
}
function remove_tree(string $dir): bool {
  if (!is_dir($dir)) return false;
  $items = scandir($dir);
  if ($items === false) return false;
  foreach ($items as $item) {
    if ($item === '.' || $item === '..') continue;
    $entry = "$dir/$item";
    if (is_dir($entry) && !is_link($entry)) {
      if (!remove_tree($entry)) return false;
    } elseif (!@unlink($entry)) {
      return false;
    }
  }
  return @rmdir($dir);
}
function language($method, $xml_file, &$error) {
  global $docroot, $boot, $plugins, $tmp;

  // parse language XML file
  $xml = file_exists($xml_file) ? @simplexml_load_file($xml_file,NULL,LIBXML_NOCDATA) : false;
  if ($xml === false) {
    $error = "XML file doesn't exist or xml parse error";
    return false;
  }
  switch ($method) {
  case 'install':
    $url = $xml->LanguageURL;
    $name = (string)$xml->LanguagePack;
    if (!valid_language_pack_name($name)) {
      $error = "invalid language pack";
      return false;
    }
    $save = "$boot/dynamix/lang-$name.zip";
    if (!file_exists($save)) {
      if ($url) {
        if (!download($url, $save, $error)) {
          @unlink($save);
          return false;
        }
      } else {
        $error = "missing URL";
        return false;
      }
    }
    $path = "$docroot/languages/$name";
    if (!is_dir($path) && !@mkdir($path, 0777, true)) {
      $error = "failed to create language directory";
      return false;
    }
    @unlink("$docroot/webGui/javascript/translate.$name.js");
    foreach (['*.dot', '*.txt', '*.json'] as $pattern) {
      foreach (glob("$path/$pattern", GLOB_NOSORT) as $lang_file) @unlink($lang_file);
    }
    $err = 0;
    $zip = new ZipArchive();
    if ($zip->open($save) === true) {
      for ($i = 0; $i < $zip->numFiles; $i++) {
        $entry = $zip->getNameIndex($i);
        if ($entry === false) continue;
        if (substr($entry, -1) === '/') continue;
        $content = $zip->getFromIndex($i);
        if ($content === false) {
          $err = 2;
          break;
        }
        $entryName = strtolower(basename($entry));
        if ($entryName === '') continue;
        if (!preg_match('/\.(dot|txt|json)$/', $entryName)) continue;
        if (file_put_contents("$path/$entryName", $content) === false) {
          $err = 2;
          break;
        }
      }
      $zip->close();
    } else {
      $err = 2;
    }
    if ($err > 1) {
      @unlink($save);
      remove_tree($path);
      $error = "unzip failed. Error code $err";
      return false;
    }
    return true;
  case 'remove':
    $name = (string)$xml->LanguagePack;
    if ($name) {
      if (!valid_language_pack_name($name)) {
        $error = "invalid language pack";
        return false;
      }
      $path = "$docroot/languages/$name";
      if (is_dir($path)) remove_tree($path);
      @unlink("$docroot/webGui/javascript/translate.$name.js");
      @unlink("$boot/lang-$name.xml");
      @unlink("$plugins/lang-$name.xml");
      @unlink("$tmp/lang-$name.xml");
      @unlink("$boot/dynamix/lang-$name.zip");
      return true;
    } else {
      $error = "missing language pack";
      return false;
    }
  case 'dump':
    // dump file: debugging
    write(print_r($xml,true));
    return true;
  default:
    // return single attribute
    $error = "$method attribute not present";
    return $xml->$method ?: false;
  }
}
