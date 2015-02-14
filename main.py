#!/usr/bin/env python
#-*- coding: utf-8 –*-

'分词&词频统计'

__author__ = 'Wang Junqi'

import entity;
import re;
import os;
import pickle;

#构建字典
def Creat_words(file_name):
    f = open(file_name,'r');
    dir_word={};
    dir_pin={};
    for line in f.readlines():
        line=line.rstrip('\n');
        line=line.rstrip('\r');
        temp_list=line.split('\t');
        name=temp_list[0];
        pin=temp_list[1];
        pin=re.sub(r'[0-9 ]','',pin);
        pin=re.sub(r'u:','v',pin);
        dir_word[name]=entity.word(name);
        if dir_pin.has_key(pin):
            dir_pin[pin].append(name);
        else:
            dir_pin[pin]=[name];
    f.close();
    return dir_word,dir_pin;


#反向最大匹配
def Segment(dir_word,essay,max_length):
    sum=0;
    essay=essay.decode('gb2312','ignore');
    essay=essay.replace('\n','');
    whole_list=re.split(ur"[^\u4e00-\u9fa5]",essay);
    whole_list=[x.encode('gb2312') for x in whole_list if x!=u''];
    # essay='\n'.join(whole_list);
    for sent in whole_list:
        sent_length=len(sent);
        end=sent_length;
        if sent_length<=max_length:
            begin=0;
        else:
            begin=end-max_length;
        temp_word_list=[];
        while end!=0:
            if dir_word.has_key(sent[begin:end]):
                word_length=end-begin;
                dir_word[sent[begin:end]].freq+=1;
                temp_word_list.append(sent[begin:end]);
                end=begin;
                if end-max_length<=0:
                    begin=0;
                else:
                    begin=end-max_length;
            else:
                if begin+2==end:
                    end=begin;
                    if end-max_length<=0:
                        begin=0;
                    else:
                        begin=end-max_length;
                else:
                    begin+=2;
        temp_sum=len(temp_word_list);
        sum+=temp_sum;
        if not temp_sum==1:
            temp_word_list.reverse();
            for x in xrange(len(temp_word_list)-1):
                if dir_word[temp_word_list[x]].bigram.has_key(temp_word_list[x+1]):
                    dir_word[temp_word_list[x]].bigram[temp_word_list[x+1]]+=1;
                else:
                    dir_word[temp_word_list[x]].bigram[temp_word_list[x+1]]=1;
    return sum;
            
#词频统计
def Segment_all(dir_word,max_length):
    sum=0;
    for essay in os.listdir('96'):
        f=open('96/'+essay,'r');
        whole_str=f.read();
        f.close();
        temp_sum=Segment(dir_word,whole_str,max_length);
        sum+=temp_sum;
    return sum;

#清理字典
def Clear_dir(dir_word):
    for key in dir_word.keys():
        if dir_word[key].freq==0:
            del(dir_word[key]);

            
#输出unigram 频数统计            
def Out_file_wordfreq(dir_word,file_name):
    temp_list=sorted(dir_word.keys(),key=lambda x:dir_word[x].freq,reverse=True);
    f=open(file_name,'w');
    for word in temp_list:
        f.write(dir_word[word].name+'\t'+str(dir_word[word].freq)+'\n');
    f.close();

#输出bigram 频数统计    
def Out_file_bigramfreq(dir_word,file_name):
    temp_dir={};
    for key in dir_word.keys():
        if len(dir_word[key].bigram)==0:
            continue;
        for bi in dir_word[key].bigram.keys():
            temp_dir[key+' '+bi]=dir_word[key].bigram[bi];
    temp_list=sorted(temp_dir.keys(),key=lambda x:temp_dir[x],reverse=True);
    f=open(file_name,'w');
    for x in temp_list:
        f.write(x+' '+str(temp_dir[x])+'\n');
    f.close();

    
#数据平滑
def Smoothing(dir_word,num_word,sum_word,theta):
    for key in dir_word.keys():
        for bi_key in dir_word[key].bigram.keys():
            temp_freq=dir_word[key].bigram[bi_key];
            temp_freq=1.0*(temp_freq+theta)/(dir_word[key].freq+num_word*theta);
            dir_word[key].bigram[bi_key]=temp_freq;
        temp_freq=dir_word[key].freq;
        temp_freq=1.0*(temp_freq+theta*num_word)/(sum_word);
        dir_word[key].freq=temp_freq;

#音字转换
def Transform_to_word(pin,dir_pin,dir_word,sum_word,theta):
    pin=pin.lower();
    length_pin=len(pin);
    keep_num=0;
    if length_pin>40:
        keep_num=10; 
    else:
        keep_num=20;        
    dp_list=[[{} for j in xrange(length_pin)] for i in xrange(length_pin)];
    for i in xrange(length_pin):
        for j in xrange(length_pin-i):
            if dir_pin.has_key(pin[j:i+j+1]):
                for word in dir_pin[pin[j:i+j+1]]:
                    temp_list=[word,word,dir_word[word].freq];
                    dp_list[j][i+j][word]=temp_list;
            for k in xrange(i):
                if dp_list[j][j+k]!={} and dp_list[j+k+1][j+i]!={}:
                    dict1=dp_list[j][j+k];
                    dict2=dp_list[j+k+1][j+i];
                    for key1 in dict1.keys():
                        for key2 in dict2.keys():
                            temp_string=key1+key2;
                            temp_p=dict1[key1][2]/(dir_word[dict2[key2][0]].freq);
                            p_link=0;
                            if dir_word[dict1[key1][1]].bigram.has_key(dict2[key2][0]):
                                p_link=dir_word[dict1[key1][1]].bigram[dict2[key2][0]]*(dir_word[dict1[key1][1]].freq**2)*dir_word[dict2[key2][0]].freq;
                            else:
                                p_link=theta/(sum_word)*dir_word[dict1[key1][1]].freq*dir_word[dict2[key2][0]].freq;
                            temp_p*=p_link*dict2[key2][2];
                            if dp_list[j][i+j].has_key(temp_string):
                                if dp_list[j][i+j][temp_string][2]<temp_p:
                                    dp_list[j][i+j][temp_string][2]=temp_p;
                            else:
                                temp_list=[dict1[key1][0],dict2[key2][1],temp_p];
                                dp_list[j][i+j][temp_string]=temp_list;
            if len(dp_list[j][i+j])>keep_num:
                temp_list=sorted(dp_list[j][i+j].keys(),key=lambda x:dp_list[j][i+j][x][2])[:-keep_num];
                for x in temp_list:
                    del(dp_list[j][i+j][x]);
    return dp_list[0][length_pin-1];

def test(pin):
    pro_dict=Transform_to_word(pin,dir_pin,dir_word,sum_word,theta);
    temp_list=sorted(pro_dict.keys(),key=lambda x:pro_dict[x][2],reverse=True);
    if len(temp_list)==0:
        print 'Please check your pinyin string.';
        return;
    for x in temp_list:
        print (str(x)+' '+str(pro_dict[x][2])).decode('gb2312');
    
dir_word,dir_pin=Creat_words('lexicon.txt');
print ' ';
print 'Creating words_dictionary...Please wait for about one minute.';
max_length=max([len(x.name) for x in dir_word.values()]);
sum_word=Segment_all(dir_word,max_length);
num_word=len(dir_word);
theta=0.2;
sum_word+=theta*(num_word**2);

#Out_file_wordfreq(dir_word,'word_freq.txt');
#Out_file_bigramfreq(dir_word,'Bigram_freq.txt');
Smoothing(dir_word,num_word,sum_word,theta);
f_word=open('__f_word','wb');
pickle.dump(dir_word,f_word);
#dir_word=pickle.load(f_word);
f_word.close();
f_pin=open('__f_pin','wb');
pickle.dump(dir_pin,f_pin);
#dir_pin=pickle.load(f_pin);
f_pin.close();
f_sum=open('__f_sum','wb');
pickle.dump(sum_word,f_sum);
#sum_word=pickle.load(f_sum);
f_sum.close();
print ' ';
print "Succeed! Enter 'exit' for quit the system.";
while 1:
    print ' ';
    str_pin=raw_input('Please enter a pinyin string:');
    if str_pin=='exit':
        break;
    test(str_pin);
    print ' ';
print 'Thank you for using!';
