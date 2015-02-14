#!/usr/bin/env python
# -*- coding: utf-8 -*-

' 从语料库中构建词表 '

__author__ = 'Wang Junqi'

import os;
import re;
from word import Word;
#读入停止词
f=open('Stop_Words.txt','r');
stop_word=f.readlines();
stop_word=[x.rstrip() for x in stop_word];
stop_word={x:0 for x in stop_word};
#构建词表
num_essay=0;
classification={};
classification_num={};#记录每个类别的文档数
class_index=0;
word_dir={};
for dir in os.listdir('training'):
	classification.setdefault(dir,class_index);
	class_index+=1;
	for essay in os.listdir('training/'+dir):
		if not classification_num.has_key(dir):
			classification_num.setdefault(dir,1);
		else:
			classification_num[dir]+=1;
		num_essay+=1;
		is_count={};#记录文章内出现的词
		f=open('training/'+dir+'/'+essay,'r');
		whole_str=f.read();
		f.close();
		whole_list=re.split(r'[^a-z^A-z]',whole_str);
		whole_list=[x.lower() for x in whole_list if x.isalpha()];
		for x in whole_list:
			if (not word_dir.has_key(x)):
				if not stop_word.has_key(x):
					temp_word=Word(x);
					setattr(temp_word,dir,1);
					word_dir[x]=temp_word;
					is_count.setdefault(x,0);
			else:
				if not is_count.has_key(x):
					if hasattr(word_dir[x],dir):
						setattr(word_dir[x],dir,1+getattr(word_dir[x],dir));
					else:
						setattr(word_dir[x],dir,1);
					word_dir[x].count_essay+=1;
					is_count.setdefault(x,0);
				word_dir[x].count+=1;
word_dir={x:y for x,y in word_dir.iteritems() if y.count>=5};#去低频词
for x,y in word_dir.iteritems():
	for c in classification.keys():
		if not hasattr(y,c):
			setattr(y,c,0);
	y.entropy=y.calculate_C(classification,classification_num,num_essay);
word_list=sorted(word_dir.values(),cmp=lambda x,y:cmp(x.entropy,y.entropy),reverse=True)[:2000];#选取特征维数s
# print [x.entropy for x in word_list];
f=open('Words_Info.txt','w');
word_index=0;
for x in word_list:
	f.write(x.name+' '+str(word_index)+' '+str(x.count)+' '+str(x.count_essay));
	for c in classification.keys():
		f.write(' '+str(getattr(x,c)));
	f.write(' '+str(x.entropy));
	f.write('\n');
	word_index+=1;
f.close();
f=open('information.txt','w');
for x,y in classification_num.iteritems():
	f.write(x+' '+str(y)+'\n');
f.close();
		