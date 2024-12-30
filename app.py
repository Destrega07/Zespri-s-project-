import streamlit as st  
import pandas as pd  
import plotly.graph_objects as go  
from data_processor import process_data  # 确保这行导入存在  

# 设置页面样式  
st.set_page_config(page_title="门店数据分析", layout="wide")  

# 自定义标题样式  
def custom_title(text):  
    st.markdown(f'<h2 style="font-family: Arial; font-size: 24px;">{text}</h2>', unsafe_allow_html=True)  

def create_area_interval(area):  
    if area > 4:  
        return 'area>4'  
    elif 2 < area <= 4:  
        return '2<area≤4'  
    elif 1.5 < area <= 2:  
        return '1.5<area≤2'  
    elif 1 <= area <= 1.5:  
        return '1≤area≤1.5'  
    else:  
        return '0≤area<1'  

def calculate_percentage_distribution(df, group_col):  
    # 计算每个组合的面积总和  
    area_sums = df.groupby(['陈列面积区间', group_col])['Zespri陈列面积'].sum()  
    
    # 计算每个组内的百分比  
    dist = area_sums.unstack()  
    dist = dist.fillna(0)  
    
    # 计算百分比  
    dist = (dist / dist.sum() * 100).round(0).astype(int)  
    
    # 确保行顺序正确  
    interval_order = ['0≤area<1', '1≤area≤1.5', '1.5<area≤2', '2<area≤4', 'area>4']  
    dist = dist.reindex(interval_order)  
    
    return dist  

def create_stacked_bar_chart(table6):  
    interval_order = ['0≤area<1', '1≤area≤1.5', '1.5<area≤2', '2<area≤4', 'area>4']  
    colors = ['rgb(141, 211, 199)', 'rgb(190, 186, 218)', 'rgb(251, 128, 114)',   
              'rgb(128, 177, 211)', 'rgb(253, 180, 98)']  

    fig = go.Figure()  
    
    for i, interval in enumerate(reversed(interval_order)):  
        values = table6.loc[interval]  
        fig.add_trace(go.Bar(  
            name=interval,  
            x=table6.columns,  
            y=values,  
            marker_color=colors[len(interval_order)-1-i],  
            text=values.apply(lambda x: f'{x}%'),  
            textposition='inside',  
            textfont=dict(  
                size=14,  
                color='black'  
            ),  
        ))  

    fig.update_layout(  
        title=None,  
        barmode='stack',  
        showlegend=True,  
        legend=dict(  
            orientation="h",  
            yanchor="bottom",  
            y=-0.2,  
            xanchor="center",  
            x=0.5  
        ),  
        plot_bgcolor='white',  
        yaxis=dict(  
            title=dict(  
                text='陈列面积分布',  
                font=dict(  
                    size=14,  
                    color='gray'  
                )  
            ),  
            range=[0, 100],  
            showticklabels=True,  
            showgrid=False,  
            tickformat='.0f'  
        ),  
        height=700,  
        margin=dict(l=50, r=50, t=30, b=100)  
    )  

    return fig

def style_table1(df):  
    # 添加总计列  
    df['总计'] = df[['Hyper', 'New Retail', 'Super']].sum(axis=1)  
    
    # 添加总计行  
    totals = df.sum(numeric_only=True)  
    totals['区域'] = '总计'  
    df = pd.concat([df, pd.DataFrame([totals])], ignore_index=True)  
    
    # 设置样式  
    styled_df = df.style\
        .format({col: '{:.0f}' for col in df.columns if col != '区域'})\
        .apply(lambda x: ['background-color: #FFEB9C' if x.name == len(df)-1 else '' for i in x], axis=1)\
        .apply(lambda x: ['background-color: #FFEB9C' if i == len(df.columns)-1 else '' for i in range(len(df.columns))], axis=1)  
    
    return styled_df  

def style_table3(df):  # 移除了未使用的table2参数  
    # 只保留需要的列  
    df = df[['商超', '门店数量', '完美门店总分', '陈列位置', '产品品类', '包装', '店内沟通']]  
    
    # 添加总计行  
    total_row = pd.Series({  
        '商超': '总计',  
        '门店数量': df['门店数量'].sum(),  
        '完美门店总分': df['完美门店总分'].mean(),  
        '陈列位置': df['陈列位置'].mean(),  
        '产品品类': df['产品品类'].mean(),  
        '包装': df['包装'].mean(),  
        '店内沟通': df['店内沟通'].mean()  
    })  
    df = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)  
    
    # 设置样式  
    styled_df = df.style\
        .format({  
            '门店数量': '{:.0f}',  
            '完美门店总分': '{:.1f}',  
            '陈列位置': '{:.1f}',  
            '产品品类': '{:.1f}',  
            '包装': '{:.1f}',  
            '店内沟通': '{:.1f}'  
        })\
        .apply(lambda x: ['background-color: #FFEB9C' if x.name == len(df)-1 else '' for i in x], axis=1)  
    
    return styled_df  

# 文件上传和数据处理  
uploaded_file = st.file_uploader("请上传Excel文件", type=['xlsx'])  

if uploaded_file is not None:  
    # 读取数据  
    df = pd.read_excel(uploaded_file, sheet_name="原始数据")  
    
    # 处理数据  
    table1, table2, table3 = process_data(df)  
    
    # 使用自定义标题样式  
    custom_title("表1：样本量统计")  
    st.dataframe(style_table1(table1), hide_index=True)  
    
    custom_title("表3：完美门店评分统计")  
    st.dataframe(style_table3(table3), hide_index=True)  
    
    # 添加陈列面积区间  
    df['陈列面积区间'] = df['Zespri陈列面积'].apply(create_area_interval)  
    channel_dist = calculate_percentage_distribution(df, '活动类别/门店类型2')  
    region_dist = calculate_percentage_distribution(df, '区域')  
    table6 = pd.concat([channel_dist, pd.DataFrame(columns=['']), region_dist], axis=1)  
    
    # 使用自定义标题样式  
    custom_title("图1：陈列面积分布图")  
    fig = create_stacked_bar_chart(table6)  
    st.plotly_chart(fig, use_container_width=True)