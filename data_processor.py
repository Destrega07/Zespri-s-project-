import pandas as pd  

def process_data(df):  
    # 创建门店类型映射  
    df['活动类别/门店类型2'] = df['活动类别/门店类型'].map({  
        '仓储': 'Hyper',  
        '普通超市': 'Hyper',  
        '高端超市': 'Super',  
        '新零售': 'New Retail'  
    })  
    
    # 生成表1数据  
    table1 = df.pivot_table(  
        values='门店名称',  
        index='区域',  
        columns='活动类别/门店类型2',  
        aggfunc='count',  
        fill_value=0  
    ).reset_index()  
    
    # 定义评分指标  
    metrics = [  
        '完美门店总分',  
        '评分_佳沛主陈列位于生鲜区主通道上，货品陈列面积不小于(水果店0.75平米​、商超1平米）',  
        '评分_是否紧挨着TOP6的水果品类陈列',  
        '评分_佳沛陈列与当地Top水果品牌位于同一区域',  
        '评分_有金果分销（盒装）',  
        '评分_有绿果分销',  
        '评分_分销盒装产品',  
        '评分_佳沛POSM物料是否可见'  
    ]  
    
    # 生成表2数据  
    table2 = df.groupby('活动类别/门店类型2').agg(  
        门店数量=('门店名称', 'count'),  
        **{metric: (metric, 'mean') for metric in metrics}  
    ).reset_index()  
    
    # 生成表3数据  
    table3 = pd.DataFrame({  
        '商超': table2['活动类别/门店类型2'],  
        '门店数量': table2['门店数量'],  
        '完美门店总分': table2['完美门店总分'],  
        '陈列位置': table2[[  
            '评分_佳沛主陈列位于生鲜区主通道上，货品陈列面积不小于(水果店0.75平米​、商超1平米）',  
            '评分_是否紧挨着TOP6的水果品类陈列',  
            '评分_佳沛陈列与当地Top水果品牌位于同一区域'  
        ]].sum(axis=1),  # 改为sum  
        '产品品类': table2[['评分_有金果分销（盒装）', '评分_有绿果分销']].sum(axis=1),  # 改为sum  
        '包装': table2['评分_分销盒装产品'],  
        '店内沟通': table2['评分_佳沛POSM物料是否可见']  
    })  
    
    return table1, table2, table3