<?php
// Copyright 2005-2023, Lime Technology
// Copyright 2012-2023, Bergware International. GPL-2.0-only.
// Source: unraid/webgui 975475904af36845053e3f96bd7a84f85fd2a969
// Exact parser functions from unraid/webgui, GPL-2.0-only.
function parse_lang_file($file) {
  // parser for translation files, includes some trickery to handle PHP quirks.
  return array_safe((array)parse_ini_string(preg_replace(['/^\s*?(null|yes|no|true|false|on|off|none)\s*?=/mi','/^\s*?([^>].*?)\s*?=\s*?(.*)\s*?$/m','/^:(.+_(help|plug)):$/m','/^:end$/m'],['$1.=','$1="$2"','_$1="','"'],escapeQuotes(file_get_contents($file)))));
}
function parse_help_file($file) {
  // parser for help text files, includes some trickery to handle PHP quirks.
  $text = array_tags((array)parse_ini_string(preg_replace(['/^$/m','/^([^:;].+)$/m','/^:(.+_help(_\d{8})?):$/m','/^:end$/m'],['>','>$1','_$1="','"'],escapeQuotes(file_get_contents($file)))));
  return array_help($text);
}
function array_safe($array) {
  // remove potential dangerous tags
  return array_filter($array,function($v,$k){
    return strlen($v) && !preg_match('#<(script|iframe)(.*?)>(.+?)</(script|iframe)>|<(link|meta)\s(.+?)/?>#is',html_entity_decode($v));
  },ARRAY_FILTER_USE_BOTH);
}
function array_tags($array) {
  // filter outdated help tags
  return array_filter($array,function($v,$k){
    $tag = explode('_',$k);
    $tag = end($tag);
    return ($tag=='help' ? true : $tag <= $_SESSION['buildDate']) && strlen($v);
  },ARRAY_FILTER_USE_BOTH);
}
function array_help(&$array) {
  // select latest applicable help
  foreach ($array as $key => $val) {
    $tag = explode('_',$key);
    if (end($tag)=='help') continue;
    $array[implode('_',array_slice($tag,0,-1))] = $array[$key];
    unset($array[$key]);
  }
  return $array;
}
function escapeQuotes($text) {
  // escape double quotes
  return str_replace(["\"\n",'"'],["\" \n",'\"'],$text);
}
