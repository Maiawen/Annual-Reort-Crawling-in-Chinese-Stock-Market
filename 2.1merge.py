import pandas as pd

#pd.set_option('max_columns', 100)
#pd.set_option('max_colwidth', 100)
pd.options.display.max_columns=100
pd.options.display.max_colwidth=100

df1=pd.read_excel('aim_data.xlsx',dtype={'code':str})
df2=pd.read_excel('all_url_data.xlsx',dtype={'code':str})

df3=pd.merge(df1,df2,on=['code','year'],how='left')#这个可以选取目标的公司

df4=df3.loc[:,['code','firm','year','pdf_url']]
df4.to_excel('merged_data.xlsx',index=False)

print(df4)
