// Register one owner-confirmed published article against the current site feed.
// No Naver login, requests, posting, deployment or personal-record changes.
const fs=require('node:fs'),path=require('node:path');
const E=require('../editorials.js');
const args=process.argv.slice(2);
function arg(name){const i=args.indexOf(name);if(i<0||!args[i+1])throw Error('Missing '+name);return args[i+1];}
const input=JSON.parse(fs.readFileSync(arg('--input'),'utf8'));
const feed=JSON.parse(fs.readFileSync(arg('--feed'),'utf8'));
if(feed.isSample!==false||!Array.isArray(feed.items))throw Error('Complete operational feed required');
const row=feed.items.find(p=>p.id===input.benefitId);
if(!row||input.sourceKey!==E.sourceKey(row))throw Error('Exact source edition required; regenerate metadata after source change');
if(input.publicationVerified!==true)throw Error('Actual publication confirmation required');
const now=new Date();
const article={...input,status:'published'};
if(!E.find(row,{version:1,articles:[article]},now))throw Error('Unverified, expired, wrong scope, or unsafe article');
const output=arg('--output'),registry=JSON.parse(fs.readFileSync(output,'utf8'));
if(registry.version!==1||!Array.isArray(registry.articles))throw Error('Invalid existing registry');
// Keep earlier editions as history; never select two editions arbitrarily.
const articles=registry.articles.map(a=>a.benefitId===row.id&&a.status==='published'?{...a,status:'superseded'}:a);
articles.push(article);
const tmp=output+'.tmp-'+process.pid;
fs.writeFileSync(tmp,JSON.stringify({version:1,articles},null,2)+'\n',{flag:'wx'});
fs.renameSync(tmp,output);
console.log(JSON.stringify({registered:row.id,url:article.url,publishedToSite:false}));
