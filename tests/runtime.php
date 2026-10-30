<?php
// GPL-2.0-only. Runs the upstream parsers and ZIP installer in build/ only.
require __DIR__.'/native-functions.php';
require __DIR__.'/native-installer.php';
set_error_handler(function($errno,$message) { throw new Exception($message); });
function write(...$messages) { foreach ($messages as $message) echo $message; }
$root = dirname(__DIR__);
$expected = json_decode(file_get_contents($root.'/build/expected.json'), true, 512, JSON_THROW_ON_ERROR);
$parsed = [];
foreach ($expected as $file => $values) {
  if ($file === 'helptext.txt') {
    foreach (['20200101','20250101','20261030','20991231'] as $date) {
      $_SESSION['buildDate'] = $date;
      $actual = parse_help_file($root.'/'.$file);
      $chosen = array_filter($values, fn($k)=>!preg_match('/_help_\d{8}$/',$k), ARRAY_FILTER_USE_KEY);
      foreach ($values as $key=>$value) {
        if (preg_match('/^(.*_help)_(\d{8})$/',$key,$m) && $m[2] <= $date) $chosen[$m[1]]=$value;
      }
      foreach ($actual as &$value) {
        $value=implode("\n",array_map(fn($line)=>str_starts_with($line,'>')?substr($line,1):$line,explode("\n",$value)));
      }
      unset($value);
      $parsed[$file]=$actual;
      ksort($actual); ksort($chosen);
      if (array_keys($actual)!==array_keys($chosen)) throw new Exception('Help keys differ: '.$date);
      foreach ($chosen as $key=>$value) if (trim($actual[$key])!==trim($value)) throw new Exception('Help value differs: '.$key);
    }
  } else {
    $actual=parse_lang_file($root.'/'.$file);
    $parsed[$file]=$actual;
    ksort($actual); ksort($values);
    if (array_keys($actual)!==array_keys($values)) throw new Exception('Keys differ: '.$file);
    foreach ($values as $key=>$value) if (trim($actual[$key])!==trim($value)) throw new Exception('Value differs: '.$file.' '.$key);
  }
}
$source=[];
foreach ($parsed as $file=>$values) if (str_starts_with(basename($file),'javascript')) $source=array_merge($source,$values);
$script=['function _(t){var l=[];'];
foreach ($source as $key => $value) $script[] = "l[\"$key\"]=\"$value\";";
$script[] = "return l[t.replace(/\&amp;|[\?\{\}\|\&\~\!\[\]\(\)\/\\:\*^\.\"']|<.+?\/?>/g,'').replace(/  +/g,' ')]||t;}";
file_put_contents($root.'/build/translate.zh_CN.js',implode($script));
file_put_contents($root.'/build/javascript-values.json',json_encode($source,JSON_UNESCAPED_UNICODE|JSON_PRETTY_PRINT));
$fixture=$root.'/build/installer-fixture';
$docroot=$fixture.'/emhttp'; $boot=$fixture.'/boot/config/plugins';
$plugins=$fixture.'/var/log/plugins'; $tmp=$fixture.'/tmp/plugins';
foreach ([$docroot.'/webGui/javascript',$docroot.'/languages/zh_CN',$boot.'/dynamix',$plugins,$tmp] as $dir) if (!is_dir($dir)) mkdir($dir,0777,true);
copy($root.'/dist/zh_CN.zip',$boot.'/dynamix/lang-zh_CN.zip');
file_put_contents($docroot.'/languages/zh_CN/stale.dot','stale');
file_put_contents($docroot.'/webGui/javascript/translate.zh_CN.js','stale');
$error='';
if (!language('install',$root.'/dist/lang-zh_CN.xml',$error)) throw new Exception($error);
if (file_exists($docroot.'/languages/zh_CN/stale.dot') || file_exists($docroot.'/webGui/javascript/translate.zh_CN.js')) throw new Exception('Stale cache retained');
foreach ($expected as $file=>$values) {
  if (hash_file('sha256',$root.'/'.$file)!==hash_file('sha256',$docroot.'/languages/zh_CN/'.strtolower(basename($file)))) throw new Exception('Installed bytes differ: '.$file);
}
file_put_contents($root.'/build/runtime.json',json_encode(['status'=>'PASS','php'=>PHP_VERSION,'files'=>count($expected),'native_install_byte_equality'=>true,'live_Unraid_tested'=>false],JSON_PRETTY_PRINT));
echo 'PASS: official parsers, JavaScript generation and ZIP installer; PHP '.PHP_VERSION."\n";
