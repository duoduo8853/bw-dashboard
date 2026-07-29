import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(layout="wide", page_title="产销协调")

st.markdown("""
<script>
(function() {
    window.__plotlyLegendClickSetup = function() {
        var plots = document.querySelectorAll('.js-plotly-plot');
        plots.forEach(function(plot) {
            if (!plot.__legend_modified) {
                plot.__legend_modified = true;
                
                var legendGroup = plot.querySelector('.legend');
                if (legendGroup) {
                    var legendItems = legendGroup.querySelectorAll('.legenditem');
                    legendItems.forEach(function(item) {
                        var newItem = item.cloneNode(true);
                        item.parentNode.replaceChild(newItem, item);
                        
                        newItem.addEventListener('click', function(e) {
                            e.stopPropagation();
                            e.preventDefault();
                            
                            var legendText = this.querySelector('.legendtext');
                            if (legendText && plot.data) {
                                var clickedName = legendText.textContent.trim();
                                var allTraces = plot.data;
                                var clickedVisible = true;
                                
                                allTraces.forEach(function(trace) {
                                    if (trace.name === clickedName) {
                                        clickedVisible = trace.visible !== false;
                                    }
                                });
                                
                                allTraces.forEach(function(trace) {
                                    trace.visible = clickedVisible ? (trace.name === clickedName ? true : 'legendonly') : true;
                                });
                                
                                Plotly.redraw(plot);
                            }
                        });
                    });
                }
            }
        });
    };
    
    var observer = new MutationObserver(window.__plotlyLegendClickSetup);
    observer.observe(document.body, { childList: true, subtree: true });
})();
</script>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600, show_spinner=False)
def cached_load_history_data(file_path):
    xls = pd.ExcelFile(file_path)
    available_sheets = xls.sheet_names
    
    df_2026 = pd.DataFrame()
    df_2025 = pd.DataFrame()
    df_budget = pd.DataFrame()
    
    for sheet in available_sheets:
        if '2026年实际销量' in sheet or sheet == '2026年实际销量':
            df_2026 = pd.read_excel(file_path, sheet_name=sheet)
            df_2026 = reshape_data(df_2026)
        elif '2025年实际销量' in sheet or sheet == '2025年实际销量':
            df_2025 = pd.read_excel(file_path, sheet_name=sheet)
            df_2025 = reshape_data(df_2025)
        elif '2026年预算销量' in sheet or sheet == '2026年预算销量':
            df_budget = pd.read_excel(file_path, sheet_name=sheet)
            df_budget = reshape_data(df_budget)
    
    material_flavor_map = {}
    if '日产量监控' in available_sheets:
        try:
            df_daily_prod = pd.read_excel(file_path, sheet_name='日产量监控')
            material_flavor_map = df_daily_prod.groupby('物料号')['口味'].first().to_dict()
        except Exception:
            pass

    if not df_2026.empty:
        df_2026['年份'] = 2026
    if not df_2025.empty:
        df_2025['年份'] = 2025

    return df_2026, df_2025, df_budget, material_flavor_map

def reshape_data(df):
    if df.empty:
        return df
    
    date_cols = []
    for col in df.columns:
        col_str = str(col)
        try:
            pd.to_datetime(col_str)
            date_cols.append(col)
        except:
            if '/' in col_str or '-' in col_str:
                date_cols.append(col)
    
    if len(date_cols) > 0:
        df_melted = df.melt(id_vars=[col for col in df.columns if col not in date_cols], 
                           value_vars=date_cols,
                           var_name='月份',
                           value_name='销量')
        
        df_melted['月份'] = df_melted['月份'].apply(lambda x: f"{pd.to_datetime(str(x)).month}月" if pd.notna(pd.to_datetime(str(x), errors='coerce')) else str(x))
        return df_melted
    
    return df

# 手机端适配样式
st.markdown("""
<style>
/* 手机端适配 */
@media (max-width: 768px) {
    /* 缩小侧边栏宽度 */
    [data-testid="stSidebar"] {
        width: 250px !important;
    }
    
    /* 调整主内容区域 */
    .main .block-container {
        padding: 1rem !important;
    }
    
    /* 调整卡片间距 */
    [data-testid="stHorizontalBlock"] {
        gap: 0.5rem !important;
    }
    
    /* 调整垂直块间距 */
    [data-testid="stVerticalBlock"] {
        gap: 0.5rem !important;
    }
    
    /* 调整表格字体 */
    .dataframe {
        font-size: 12px !important;
    }
    
    /* 调整按钮大小 */
    .stButton > button {
        padding: 0.5rem 1rem !important;
        font-size: 14px !important;
    }
    
    /* 调整选择器高度 */
    .stSelectbox > div > div {
        height: 40px !important;
    }
    
    /* 调整多选器高度 */
    .stMultiSelect > div > div {
        min-height: 40px !important;
    }
    
    /* 调整图表容器 */
    .js-plotly-plot .plotly, .js-plotly-plot .plotly div {
        width: 100% !important;
    }
}

/* 隐藏滚动条 */
::-webkit-scrollbar {
    height: 6px;
    width: 6px;
}
::-webkit-scrollbar-thumb {
    background: #ccc;
    border-radius: 3px;
}

/* 调整整体字体 */
body {
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# 添加隐藏按钮的CSS
st.markdown("""
<style>
/* Plotly图表柱状图hover效果 */
.js-plotly-plot .plotly .bar {
    cursor: pointer !important;
}

.js-plotly-plot .plotly .bar:hover {
    opacity: 0.85 !important;
}

/* Plotly SVG元素hover效果 */
.js-plotly-plot svg g.points path:hover,
.js-plotly-plot svg g.bars rect:hover,
.js-plotly-plot svg g.points polygon:hover {
    opacity: 0.85 !important;
    cursor: pointer !important;
}

/* Plotly图表区域cursor */
.js-plotly-plot {
    cursor: pointer !important;
}

.hidden-btn {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# 初始化会话状态（仅在首次运行时初始化）
if 'show_focus_report' not in st.session_state:
    st.session_state.show_focus_report = False

# 调试：打印状态（已注释）
# st.write(f"Debug: show_focus_report = {st.session_state.show_focus_report}")

def save_page_state(page_name):
    if page_name == '需求分析':
        state_keys = [
            'region', 'dept', 'project', 'product30', 'product20',
            'capacity', 'flavor', 'package', 'show_flavor_analysis',
            'show_focus_report'
        ]
        saved_state = {}
        for key in state_keys:
            if key in st.session_state:
                saved_state[key] = st.session_state[key]
        st.session_state['saved_demand_state'] = saved_state
    elif page_name == '历史销量':
        state_keys = [
            'history_region', 'history_dept', 'history_project', 
            'history_product30', 'history_product20', 'history_flavor_new',
            'history_capacity_new', 'history_package_new', 'history_month_multi'
        ]
        saved_state = {}
        for key in state_keys:
            if key in st.session_state:
                saved_state[key] = st.session_state[key]
        st.session_state['saved_history_state'] = saved_state

def restore_page_state(page_name):
    if page_name == '需求分析':
        if 'saved_demand_state' in st.session_state:
            saved_state = st.session_state['saved_demand_state']
            for key, value in saved_state.items():
                st.session_state[key] = value
    elif page_name == '历史销量':
        if 'saved_history_state' in st.session_state:
            saved_state = st.session_state['saved_history_state']
            for key, value in saved_state.items():
                st.session_state[key] = value

@st.cache_data(ttl=3600)
def load_data():
    try:
        df_tj = pd.read_excel('BW数据.xlsx', sheet_name='出货-天津-部别')
        df_hb = pd.read_excel('BW数据.xlsx', sheet_name='出货-河北-部别')
        df = pd.concat([df_tj, df_hb], ignore_index=True)
        df['需求量'] = df['需求量'].fillna(0)
        df['去年同期销量'] = df['去年同期销量'].fillna(0)
        df['预算销量'] = df['预算销量'].fillna(0)
        df['容量'] = df['容量'].astype(str)
        df['口味'] = df['口味'].astype(str)
        return df
    except Exception as e:
        st.error(f"加载数据失败: {str(e)}")
        return pd.DataFrame()

def get_file_mod_time(filepath):
    import os
    try:
        return os.path.getmtime(filepath)
    except:
        return 0

@st.cache_data(ttl=3600)
def load_mappings(file_mod_time_bw=0, file_mod_time_rel=0):
    try:
        xls = pd.ExcelFile('BW数据.xlsx')
        
        project_map = {}
        product30_map = {}
        product20_map = {}
        material_map = {}
        
        if '专案对应关系' in xls.sheet_names:
            project_df = pd.read_excel(xls, sheet_name='专案对应关系')
            project_map = project_df.groupby('专案')['口味别'].apply(list).to_dict()
        
        if '3.0对应关系' in xls.sheet_names:
            product30_df = pd.read_excel(xls, sheet_name='3.0对应关系')
            product30_map = product30_df.groupby('3.0新品')['口味别'].apply(list).to_dict()
        
        if '2.0对应关系' in xls.sheet_names:
            product20_df = pd.read_excel(xls, sheet_name='2.0对应关系')
            product20_map = product20_df.groupby('2.0产品')['口味别'].apply(list).to_dict()
        
        import os
        if os.path.exists('对应关系.xlsx'):
            print("优先从对应关系.xlsx 加载物料对应关系")
            xls2 = pd.ExcelFile('对应关系.xlsx')
            if '物料对应关系' in xls2.sheet_names:
                material_df = pd.read_excel(xls2, sheet_name='物料对应关系')
                material_map = process_material_data(material_df)
                print(f"成功从对应关系.xlsx 加载物料映射: {len(material_map.get('flavors', []))} 口味, {len(material_map.get('capacities', []))} 容量, {len(material_map.get('packages', []))} 内包装")
        elif '物料对应关系' in xls.sheet_names:
            material_df = pd.read_excel(xls, sheet_name='物料对应关系')
            material_map = process_material_data(material_df)
        else:
            print("未找到物料对应关系数据")

        return project_map, product30_map, product20_map, material_map
    except Exception as e:
        print(f"加载映射数据失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return {}, {}, {}, {}

@st.cache_data
def precompute_flavor_materials(material_map):
    flavor_to_materials = {}
    if material_map and 'material_to_universal' in material_map and 'universal_to_attrs' in material_map:
        material_to_universal = material_map['material_to_universal']
        universal_to_attrs = material_map['universal_to_attrs']
        
        for material, universal in material_to_universal.items():
            if universal in universal_to_attrs:
                attrs = universal_to_attrs[universal]
                for flavor in attrs.get('flavors', []):
                    if flavor not in flavor_to_materials:
                        flavor_to_materials[flavor] = set()
                    flavor_to_materials[flavor].add(material)
    
    return flavor_to_materials

@st.cache_data
def precompute_capacity_materials(material_map):
    capacity_to_materials = {}
    if material_map and 'material_to_universal' in material_map and 'universal_to_attrs' in material_map:
        material_to_universal = material_map['material_to_universal']
        universal_to_attrs = material_map['universal_to_attrs']
        
        for material, universal in material_to_universal.items():
            if universal in universal_to_attrs:
                attrs = universal_to_attrs[universal]
                for capacity in attrs.get('capacities', []):
                    if capacity not in capacity_to_materials:
                        capacity_to_materials[capacity] = set()
                    capacity_to_materials[capacity].add(material)
    
    return capacity_to_materials

@st.cache_data
def precompute_package_materials(material_map):
    package_to_materials = {}
    if material_map and 'material_to_universal' in material_map and 'universal_to_attrs' in material_map:
        material_to_universal = material_map['material_to_universal']
        universal_to_attrs = material_map['universal_to_attrs']
        
        for material, universal in material_to_universal.items():
            if universal in universal_to_attrs:
                attrs = universal_to_attrs[universal]
                for package in attrs.get('packages', []):
                    if package not in package_to_materials:
                        package_to_materials[package] = set()
                    package_to_materials[package].add(material)
    
    return package_to_materials

def filter_data(df, region, dept, months, flavor, capacity, package, project, product30, product20, region_dept_map, flavor_to_materials, capacity_to_materials, package_to_materials, project_map, product30_map, product20_map, material_col=None):
    if df.empty:
        return df
    
    filtered = df
    
    if region != '全部' and '营业部' in filtered.columns:
        filtered = filtered[filtered['营业部'].isin(region_dept_map.get(region, []))]
    
    if dept != '全部' and '营业部' in filtered.columns:
        filtered = filtered[filtered['营业部'] == dept]
    
    if isinstance(months, list) and len(months) > 0 and '月份' in filtered.columns:
        filtered = filtered[filtered['月份'].isin(months)]
    
    if project != '全部' and project_map and material_col and material_col in filtered.columns:
        project_flavors = project_map.get(project, [])
        if project_flavors:
            materials_to_keep = set()
            for f in project_flavors:
                if f in flavor_to_materials:
                    materials_to_keep.update(flavor_to_materials[f])
            if materials_to_keep:
                filtered = filtered[filtered[material_col].astype(str).str.strip().isin(materials_to_keep)]
        elif '口味' in filtered.columns:
            filtered = filtered[filtered['口味'].isin(project_flavors)]
    
    if product30 != '全部' and product30_map and material_col and material_col in filtered.columns:
        product30_flavors = product30_map.get(product30, [])
        if product30_flavors:
            materials_to_keep = set()
            for f in product30_flavors:
                if f in flavor_to_materials:
                    materials_to_keep.update(flavor_to_materials[f])
            if materials_to_keep:
                filtered = filtered[filtered[material_col].astype(str).str.strip().isin(materials_to_keep)]
        elif '口味' in filtered.columns:
            filtered = filtered[filtered['口味'].isin(product30_flavors)]
    
    if product20 != '全部' and product20_map and material_col and material_col in filtered.columns:
        product20_flavors = product20_map.get(product20, [])
        if product20_flavors:
            materials_to_keep = set()
            for f in product20_flavors:
                if f in flavor_to_materials:
                    materials_to_keep.update(flavor_to_materials[f])
            if materials_to_keep:
                filtered = filtered[filtered[material_col].astype(str).str.strip().isin(materials_to_keep)]
        elif '口味' in filtered.columns:
            filtered = filtered[filtered['口味'].isin(product20_flavors)]
    
    if flavor != '全部':
        if flavor_to_materials and flavor in flavor_to_materials and material_col and material_col in filtered.columns:
            materials_to_keep = flavor_to_materials[flavor]
            filtered = filtered[filtered[material_col].astype(str).str.strip().isin(materials_to_keep)]
        elif '口味' in filtered.columns:
            filtered = filtered[filtered['口味'] == flavor]
    
    if capacity != '全部' and len(filtered) > 0:
        if '容量' in filtered.columns:
            filtered['容量'] = filtered['容量'].astype(str).str.strip()
            capacity_str = str(capacity).strip()
            filtered = filtered[filtered['容量'] == capacity_str]
        elif capacity_to_materials and capacity in capacity_to_materials and material_col and material_col in filtered.columns:
            materials_to_keep = capacity_to_materials[capacity]
            filtered = filtered[filtered[material_col].astype(str).str.strip().isin(materials_to_keep)]
    
    if package != '全部' and len(filtered) > 0:
        if package_to_materials and package in package_to_materials and material_col and material_col in filtered.columns:
            materials_to_keep = package_to_materials[package]
            filtered = filtered[filtered[material_col].astype(str).str.strip().isin(materials_to_keep)]
        elif '内包装' in filtered.columns:
            filtered = filtered[filtered['内包装'] == package]
    
    return filtered

def process_material_data(material_df):
    material_map = {}
    flavor_list = []
    capacity_list = []
    package_list = []
    
    if '口味' in material_df.columns:
        flavor_list = [str(f).strip() for f in material_df['口味'].dropna().unique() if str(f).strip()]
        print(f"从物料对应关系提取口味: {len(flavor_list)} 个")
    
    if '容量' in material_df.columns:
        capacity_list = []
        for c in material_df['容量'].dropna().unique():
            c_str = str(c).strip()
            if c_str:
                try:
                    c_int = int(float(c))
                    capacity_list.append(str(c_int))
                except:
                    capacity_list.append(c_str)
        print(f"从物料对应关系提取容量: {len(capacity_list)} 个")
    
    if '内包装' in material_df.columns:
        package_list = [str(p).strip() for p in material_df['内包装'].dropna().unique() if str(p).strip()]
        print(f"从物料对应关系提取内包装: {len(package_list)} 个")
    
    material_map = {
        'flavors': sorted(flavor_list),
        'capacities': sorted(capacity_list),
        'packages': sorted(package_list)
    }
    
    if '物料' in material_df.columns and '全国通用物料' in material_df.columns:
        material_df['物料'] = material_df['物料'].astype(str).str.strip()
        material_df['全国通用物料'] = material_df['全国通用物料'].astype(str).str.strip()
        
        material_to_universal = material_df.drop_duplicates('物料').set_index('物料')['全国通用物料'].to_dict()
        
        universal_to_attrs = {}
        for _, row in material_df.iterrows():
            universal = str(row['全国通用物料']).strip()
            if universal not in universal_to_attrs:
                universal_to_attrs[universal] = {
                    'flavors': set(),
                    'capacities': set(),
                    'packages': set()
                }
            if pd.notna(row.get('口味')):
                universal_to_attrs[universal]['flavors'].add(str(row['口味']).strip())
            if pd.notna(row.get('容量')):
                try:
                    capacity_int = int(float(row['容量']))
                    universal_to_attrs[universal]['capacities'].add(str(capacity_int))
                except:
                    universal_to_attrs[universal]['capacities'].add(str(row['容量']).strip())
            if pd.notna(row.get('内包装')):
                universal_to_attrs[universal]['packages'].add(str(row['内包装']).strip())
        
        for key in universal_to_attrs:
            universal_to_attrs[key]['flavors'] = sorted(list(universal_to_attrs[key]['flavors']))
            universal_to_attrs[key]['capacities'] = sorted(list(universal_to_attrs[key]['capacities']))
            universal_to_attrs[key]['packages'] = sorted(list(universal_to_attrs[key]['packages']))
        
        material_map['material_to_universal'] = material_to_universal
        material_map['universal_to_attrs'] = universal_to_attrs
        print(f"物料映射加载成功: {len(material_to_universal)} 物料 -> {len(universal_to_attrs)} 通用物料")
    else:
        print("物料对应关系表缺少'物料'或'全国通用物料'列")
    
    return material_map

REGION_DEPT_MAP = {
    '天津行销区域': ['天津地区部', '津东经销部', '津北经销部', '廊坊经销部', '津西经销部', '天津OT处', '天津餐饮处', '天津新零售', '天津行销公司特营处'],
    '河北行销区域': ['河北地区部', '冀东营业部', '冀西营业部', '冀南营业部', '冀北营业部', '石家庄营业部', '唐山营业部', '石家庄餐饮处', '河北行销公司特营处']
}

df = load_data()
bw_mod_time = get_file_mod_time('BW数据.xlsx')
rel_mod_time = get_file_mod_time('对应关系.xlsx')
project_map, product30_map, product20_map, material_map = load_mappings(bw_mod_time, rel_mod_time)

if 'current_page' not in st.session_state:
    st.session_state.current_page = '需求分析'

with st.sidebar:
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%) !important;
            border-right: 1px solid rgba(226, 232, 240, 0.8);
            min-height: 100vh;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
        }
        [data-testid="stSidebar"] .css-1d391kg {
            background: transparent;
        }
        [data-testid="stSidebar"] .stButton > button {
            width: calc(100% - 16px);
            margin: 10px 8px !important;
            padding: 10px 20px;
            border-radius: 14px;
            border: 1.5px solid rgba(226, 232, 240, 0.8);
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.9) 100%) !important;
            color: #334155 !important;
            font-size: 15px;
            font-weight: 500;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            text-align: left;
            letter-spacing: 0.3px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03), 0 1px 2px rgba(0, 0, 0, 0.05);
        }
        [data-testid="stSidebar"] .stButton {
            margin-bottom: 0 !important;
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            background: linear-gradient(135deg, rgba(239, 246, 255, 0.95) 0%, rgba(219, 234, 254, 0.95) 100%) !important;
            color: #1e40af !important;
            border-color: rgba(147, 197, 253, 0.8);
            transform: translateX(6px);
            box-shadow: 0 4px 16px rgba(59, 130, 246, 0.15), 0 2px 6px rgba(59, 130, 246, 0.1);
        }
        [data-testid="stSidebar"] .stButton > button.active {
            background: linear-gradient(135deg, rgba(219, 234, 254, 0.95) 0%, rgba(191, 219, 254, 0.95) 100%) !important;
            color: #1e40af !important;
            font-weight: 600;
            font-size: 15px;
            letter-spacing: 0.5px;
            border-color: rgba(59, 130, 246, 0.5);
            box-shadow: 0 4px 16px rgba(59, 130, 246, 0.18), 0 2px 6px rgba(59, 130, 246, 0.12);
        }
        .sidebar-header {
            padding: 20px 16px;
            border-bottom: 1px solid rgba(226, 232, 240, 0.8);
            background: rgba(255, 255, 255, 0.5);
        }
        .sidebar-title {
            font-size: 24px;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 4px;
        }
        .sidebar-subtitle {
            font-size: 14px;
            color: #94a3b8;
        }
        .menu-divider {
            height: 1px;
            background: linear-gradient(90deg, rgba(226, 232, 240, 0.8) 0%, transparent 100%);
            margin: 16px 8px;
        }
        .menu-section-label {
            font-size: 11px;
            font-weight: 500;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 12px 16px 8px;
            margin-top: 8px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="sidebar-header">
            <div class="sidebar-title">产销协调</div>
            <div class="sidebar-subtitle">Production & Sales</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="menu-section-label">功能菜单</div>', unsafe_allow_html=True)
    
    if st.session_state.current_page == '需求分析':
        st.markdown('<style>[data-testid="stSidebar"] [data-testid="baseButton-secondary-btn_demand"] { background-color: #eff6ff !important; color: #1e40af !important; font-weight: 600; }</style>', unsafe_allow_html=True)
    if st.button('需求分析看板（BW）', key='btn_demand', use_container_width=True):
        save_page_state(st.session_state.current_page)
        restore_page_state('需求分析')
        st.session_state.current_page = '需求分析'
        if 'show_flavor_analysis' in st.session_state:
            st.session_state.show_flavor_analysis = False
    
    if st.session_state.current_page == '历史销量':
        st.markdown('<style>[data-testid="stSidebar"] [data-testid="baseButton-secondary-btn_history"] { background-color: #eff6ff !important; color: #1e40af !important; font-weight: 600; }</style>', unsafe_allow_html=True)
    if st.button('历史销量', key='btn_history', use_container_width=True):
        save_page_state(st.session_state.current_page)
        restore_page_state('历史销量')
        st.session_state.current_page = '历史销量'
    
    if st.session_state.current_page == '产量一览':
        st.markdown('<style>[data-testid="stSidebar"] [data-testid="baseButton-secondary-btn_output"] { background-color: #eff6ff !important; color: #1e40af !important; font-weight: 600; }</style>', unsafe_allow_html=True)
    if st.button('产量一览', key='btn_output', use_container_width=True):
        st.session_state.current_page = '产量一览'
    
    if st.session_state.current_page == '营业额分析':
        st.markdown('<style>[data-testid="stSidebar"] [data-testid="baseButton-secondary-btn_revenue"] { background-color: #eff6ff !important; color: #1e40af !important; font-weight: 600; }</style>', unsafe_allow_html=True)
    if st.button('营业额分析', key='btn_revenue', use_container_width=True):
        st.session_state.current_page = '营业额分析'
    
    if st.session_state.current_page == '物料对应关系':
        st.markdown('<style>[data-testid="stSidebar"] [data-testid="baseButton-secondary-btn_material"] { background-color: #eff6ff !important; color: #1e40af !important; font-weight: 600; }</style>', unsafe_allow_html=True)
    if st.button('物料对应关系', key='btn_material', use_container_width=True):
        st.session_state.current_page = '物料对应关系'
    
    if st.session_state.current_page == '调出分析':
        st.markdown('<style>[data-testid="stSidebar"] [data-testid="baseButton-secondary-btn_adjust"] { background-color: #eff6ff !important; color: #1e40af !important; font-weight: 600; }</style>', unsafe_allow_html=True)
    if st.button('调出分析', key='btn_adjust', use_container_width=True):
        st.session_state.current_page = '调出分析'
    
    if st.session_state.current_page == '大修进度':
        st.markdown('<style>[data-testid="stSidebar"] [data-testid="baseButton-secondary-btn_maintenance"] { background-color: #eff6ff !important; color: #1e40af !important; font-weight: 600; }</style>', unsafe_allow_html=True)
    if st.button('大修进度', key='btn_maintenance', use_container_width=True):
        st.session_state.current_page = '大修进度'
    
    st.markdown('<div class="menu-divider"></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="menu-section-label">设置</div>', unsafe_allow_html=True)
    st.button('系统设置', use_container_width=True, key='btn_settings')
    st.button('退出登录', use_container_width=True, key='btn_logout')

st.markdown("""
    <style>
    html, body, #root, .stApp {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%) !important;
        min-height: 100vh !important;
    }
    [data-testid="stHeader"] {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%) !important;
        border-bottom: none !important;
    }
    [data-testid="stToolbar"] {
        background: transparent !important;
    }
    .header-card {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 50%, #3b82f6 100%);
        border-radius: 16px;
        padding: 32px;
        margin-bottom: 24px;
        box-shadow: 0 12px 40px rgba(30, 58, 138, 0.35);
    }
    .header-card-history {
        background: linear-gradient(135deg, #1a73e8 0%, #4285f4 50%, #669df6 100%);
        border-radius: 16px;
        padding: 32px;
        margin-bottom: 24px;
        box-shadow: 0 12px 40px rgba(66, 133, 244, 0.35);
    }
    .header-title {
        font-size: 32px;
        font-weight: 700;
        color: white;
        margin-bottom: 8px;
    }
    .header-subtitle {
        font-size: 14px;
        color: rgba(255, 255, 255, 0.85);
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.5);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: default;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
        background: rgba(255, 255, 255, 0.9);
        border-color: rgba(66, 133, 244, 0.3);
    }
    .metric-card-blue {
        background: rgba(239, 246, 255, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        border: 1px solid rgba(147, 197, 253, 0.5);
        box-shadow: 0 4px 20px rgba(59, 130, 246, 0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: default;
    }
    .metric-card-blue:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(59, 130, 246, 0.2);
        background: rgba(239, 246, 255, 0.9);
        border-color: rgba(59, 130, 246, 0.6);
    }
    .metric-card-green {
        background: rgba(236, 253, 245, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        border: 1px solid rgba(52, 211, 153, 0.5);
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: default;
    }
    .metric-card-green:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(16, 185, 129, 0.2);
        background: rgba(236, 253, 245, 0.9);
        border-color: rgba(16, 185, 129, 0.6);
    }
    .metric-card-orange {
        background: rgba(255, 251, 235, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        border: 1px solid rgba(251, 191, 36, 0.5);
        box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: default;
    }
    .metric-card-orange:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(245, 158, 11, 0.2);
        background: rgba(255, 251, 235, 0.9);
        border-color: rgba(245, 158, 11, 0.6);
    }
    .metric-card-red {
        background: rgba(254, 242, 242, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        border: 1px solid rgba(248, 113, 113, 0.5);
        box-shadow: 0 4px 20px rgba(239, 68, 68, 0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: default;
    }
    .metric-card-red:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(239, 68, 68, 0.2);
        background: rgba(254, 242, 242, 0.9);
        border-color: rgba(239, 68, 68, 0.6);
    }
    .metric-card-gray {
        background: rgba(243, 244, 246, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        border: 1px solid rgba(209, 213, 219, 0.5);
        box-shadow: 0 4px 20px rgba(107, 114, 128, 0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: default;
    }
    .metric-card-gray:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(107, 114, 128, 0.15);
        background: rgba(243, 244, 246, 0.9);
        border-color: rgba(107, 114, 128, 0.4);
    }
    .metric-card-purple {
        background: rgba(232, 240, 254, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        border: 1px solid rgba(138, 180, 248, 0.5);
        box-shadow: 0 4px 20px rgba(66, 133, 244, 0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: default;
    }
    .metric-card-purple:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(66, 133, 244, 0.2);
        background: rgba(232, 240, 254, 0.9);
        border-color: rgba(66, 133, 244, 0.6);
    }
    .metric-value {
        font-size: 32px;
        font-weight: 800;
        color: #1e293b;
        font-variant-numeric: tabular-nums;
        white-space: nowrap;
    }
    .metric-value-blue {
        font-size: 32px;
        font-weight: 800;
        color: #1e40af;
        font-variant-numeric: tabular-nums;
        white-space: nowrap;
    }
    .metric-value-green {
        font-size: 32px;
        font-weight: 800;
        color: #059669;
        font-variant-numeric: tabular-nums;
        white-space: nowrap;
    }
    .metric-value-orange {
        font-size: 32px;
        font-weight: 800;
        color: #d97706;
        font-variant-numeric: tabular-nums;
        white-space: nowrap;
    }
    .metric-value-red {
        font-size: 32px;
        font-weight: 800;
        color: #dc2626;
        font-variant-numeric: tabular-nums;
        white-space: nowrap;
    }
    .metric-value-gray {
        font-size: 32px;
        font-weight: 800;
        color: #9ca3af;
        font-variant-numeric: tabular-nums;
        white-space: nowrap;
    }
    .metric-value-purple {
        font-size: 32px;
        font-weight: 800;
        color: #1a73e8;
        font-variant-numeric: tabular-nums;
        white-space: nowrap;
    }
    .metric-label {
        font-size: 16px;
        color: #64748b;
        margin-top: 10px;
        font-weight: 600;
    }
    .metric-trend {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-top: 4px;
        font-size: 12px;
        font-weight: 600;
    }
    .section-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
        margin-bottom: 24px;
        border: 1px solid rgba(255, 255, 255, 0.6);
    }
    .section-title {
        font-size: 20px;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 20px;
        border-left: 4px solid #3b82f6;
        padding-left: 12px;
        background: rgba(239, 246, 255, 0.8);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        padding-top: 8px;
        padding-bottom: 8px;
        margin-left: -24px;
        padding-left: 28px;
        margin-right: -24px;
    }
    .section-title-purple {
        font-size: 20px;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 20px;
        border-left: 4px solid #4285f4;
        padding-left: 12px;
        background: rgba(232, 240, 254, 0.8);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        padding-top: 8px;
        padding-bottom: 8px;
        margin-left: -24px;
        padding-left: 28px;
        margin-right: -24px;
    }
    .custom-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        border: 1px solid rgba(229, 231, 235, 0.8);
        border-radius: 8px;
        overflow: hidden;
        font-size: 14px;
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
    }
    .custom-table th {
        background: rgba(243, 244, 246, 0.9);
        color: #374151;
        font-weight: 600;
        padding: 12px 10px;
        text-align: center;
        border-bottom: 1px solid rgba(229, 231, 235, 0.8);
        border-right: 1px solid rgba(229, 231, 235, 0.8);
        position: sticky;
        top: 0;
        z-index: 1;
    }
    .custom-table th:last-child {
        border-right: none;
    }
    .custom-table td {
        padding: 10px 8px;
        text-align: center;
        border-bottom: 1px solid rgba(243, 244, 246, 0.8);
        border-right: 1px solid rgba(243, 244, 246, 0.8);
        color: #374151;
    }
    .custom-table td:last-child {
        border-right: none;
    }
    .custom-table tbody tr:last-child td {
        border-bottom: none;
    }
    .custom-table tbody tr:hover {
        background: rgba(59, 130, 246, 0.08);
    }
    .stSelectbox [data-baseweb="select"] > div {
        background: #F8FAFC !important;
        border: 1px solid rgba(0, 0, 0, 0.06) !important;
        border-radius: 8px;
        transition: all 0.2s ease !important;
    }
    .stSelectbox [data-baseweb="select"]:hover > div {
        background: #F0F7FF !important;
        border-color: rgba(66, 133, 244, 0.3) !important;
        box-shadow: 0 2px 8px rgba(66, 133, 244, 0.1) !important;
    }
    .stMultiSelect [data-baseweb="select"] > div {
        background: #F8FAFC !important;
        border: 1px solid rgba(0, 0, 0, 0.06) !important;
        border-radius: 8px;
        transition: all 0.2s ease !important;
    }
    .stMultiSelect [data-baseweb="select"]:hover > div {
        background: #F0F7FF !important;
        border-color: rgba(66, 133, 244, 0.3) !important;
        box-shadow: 0 2px 8px rgba(66, 133, 244, 0.1) !important;
    }
    </style>
    """, unsafe_allow_html=True)

if st.session_state.current_page == '需求分析':
    import os
    from datetime import datetime
    
    file_path = 'BW数据.xlsx'
    update_time = '未知'
    if os.path.exists(file_path):
        mtime = os.path.getmtime(file_path)
        update_time = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
    
    st.markdown("""
        <div class='header-card'>
            <div class='header-title'>需求分析看板（BW）</div>
            <div class='header-subtitle'>实时数据分析与可视化平台 | 基于出货-天津/河北部别数据</div>
            <div style='font-size: 12px; color: rgba(255, 255, 255, 0.7); margin-top: 8px;'>数据更新时间: {update_time}</div>
        </div>
        """.format(update_time=update_time), unsafe_allow_html=True)

    clear_filters = st.session_state.get('clear_filters', False)
    if clear_filters:
        st.session_state['region'] = '全部'
        st.session_state['dept'] = '全部'
        st.session_state['project'] = '全部'
        st.session_state['product30'] = '全部'
        st.session_state['product20'] = '全部'
        st.session_state['capacity'] = '全部'
        st.session_state['flavor'] = '全部'
        st.session_state['package'] = '全部'
        st.session_state['clear_filters'] = False
        st.rerun()

    upload_col, _ = st.columns([3, 7])
    with upload_col:
        uploaded_file = st.file_uploader(
            '📁 上传Excel数据',
            type=['xlsx', 'xls'],
            key=f'page_file_uploader_{st.session_state.get("upload_counter", 0)}',
            help='上传包含出货数据的Excel文件',
            label_visibility='collapsed',
            on_change=lambda: st.session_state.update({'data_updated': True})
        )
        
        if uploaded_file is not None and st.session_state.get('data_updated'):
            try:
                with open('BW数据.xlsx', 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                
                st.cache_data.clear()
                
                if 'upload_counter' not in st.session_state:
                    st.session_state.upload_counter = 0
                st.session_state.upload_counter += 1
                
                st.session_state['data_updated'] = False
                st.session_state['last_upload_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                st.success(f'✅ 数据上传成功！({st.session_state["last_upload_time"]})')
            except Exception as e:
                st.error(f'❌ 上传失败: {str(e)}')

    col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns([0.8, 0.8, 0.9, 0.9, 0.9, 0.8, 1.0, 0.7, 0.9, 0.9])

    with col1:
        region = st.selectbox('行销区域别', ['全部'] + list(REGION_DEPT_MAP.keys()), key='region')

    with col2:
        if region == '全部':
            all_depts = []
            for depts in REGION_DEPT_MAP.values():
                all_depts.extend(depts)
            dept_options = ['全部'] + list(set(all_depts) & set(df['营业部'].unique()))
        else:
            dept_options = ['全部'] + [d for d in REGION_DEPT_MAP[region] if d in df['营业部'].unique()]
        dept = st.selectbox('营业部', dept_options, key='dept')

    with col3:
        project_options = ['全部'] + list(project_map.keys())
        project = st.selectbox('专案', project_options, key='project')

    with col4:
        product30_options = ['全部'] + list(product30_map.keys())
        product30 = st.selectbox('3.0新品', product30_options, key='product30')

    with col5:
        product20_options = ['全部'] + list(product20_map.keys())
        product20 = st.selectbox('2.0产品', product20_options, key='product20')

    filtered_for_flavor = df.copy()
    if region != '全部':
        filtered_for_flavor = filtered_for_flavor[filtered_for_flavor['营业部'].isin(REGION_DEPT_MAP[region])]
    if dept != '全部':
        filtered_for_flavor = filtered_for_flavor[filtered_for_flavor['营业部'] == dept]

    material_flavors = material_map.get('flavors', [])
    material_capacities = material_map.get('capacities', [])
    material_packages = material_map.get('packages', [])

    if material_flavors:
        available_flavors = sorted(set(filtered_for_flavor['口味'].unique()) & set(material_flavors))
    else:
        flavor_stats = filtered_for_flavor.groupby('口味').agg({
            '需求量': 'sum',
            '月累排单': 'sum',
            '去年同期销量': 'sum',
            '预算销量': 'sum'
        }).reset_index()
        available_flavors = flavor_stats[
            (flavor_stats['需求量'] > 0) | 
            (flavor_stats['月累排单'] > 0) | 
            (flavor_stats['去年同期销量'] > 0) | 
            (flavor_stats['预算销量'] > 0)
        ]['口味'].tolist()
    
    if project != '全部':
        available_flavors = [f for f in available_flavors if f in project_map.get(project, [])]
    if product30 != '全部':
        available_flavors = [f for f in available_flavors if f in product30_map.get(product30, [])]
    if product20 != '全部':
        available_flavors = [f for f in available_flavors if f in product20_map.get(product20, [])]

    available_flavors = ['全部'] + sorted(available_flavors)
    
    if 'flavor' in st.session_state and st.session_state['flavor'] != '全部' and st.session_state['flavor'] not in available_flavors:
        st.session_state['flavor'] = '全部'

    with col7:
        flavor = st.selectbox('口味', available_flavors, key='flavor')

    with col6:
        if material_map.get('universal_to_attrs') and flavor != '全部':
            capacity_set = set()
            for universal, attrs in material_map['universal_to_attrs'].items():
                flavors = attrs.get('flavors', [])
                if flavor in flavors:
                    capacities = attrs.get('capacities', [])
                    capacity_set.update(capacities)
            available_capacities = ['全部'] + sorted([c for c in capacity_set if c])
        elif material_capacities:
            available_capacities = ['全部'] + sorted(set(filtered_for_flavor['容量'].unique()) & set(material_capacities))
        else:
            available_capacities = ['全部'] + sorted(filtered_for_flavor['容量'].unique())
        if 'capacity' in st.session_state and st.session_state['capacity'] != '全部' and st.session_state['capacity'] not in available_capacities:
            st.session_state['capacity'] = '全部'
        capacity = st.selectbox('容量', available_capacities, key='capacity')

    with col8:
        if material_map.get('universal_to_attrs') and flavor != '全部':
            package_set = set()
            for universal, attrs in material_map['universal_to_attrs'].items():
                flavors = attrs.get('flavors', [])
                if flavor in flavors:
                    packages = attrs.get('packages', [])
                    package_set.update(packages)
            available_packages = ['全部'] + sorted([p for p in package_set if p])
        elif material_packages:
            available_packages = ['全部'] + sorted(set(filtered_for_flavor.get('内包装', []).unique()) & set(material_packages))
        else:
            available_packages = ['全部'] + sorted(filtered_for_flavor.get('内包装', []).unique())
        if 'package' in st.session_state and st.session_state['package'] != '全部' and st.session_state['package'] not in available_packages:
            st.session_state['package'] = '全部'
        package = st.selectbox('内包装', available_packages, key='package')

    def check_flavor_and_show_analysis():
        if st.session_state.get('flavor', '全部') == '全部':
            st.session_state['show_flavor_warning'] = True
        else:
            st.session_state['show_flavor_warning'] = False
            st.session_state['show_flavor_analysis'] = True

    with col9:
        st.markdown('<div style="margin-top: 25px;"></div>', unsafe_allow_html=True)
        st.button('🔍 达成分析', key='btn_flavor_analysis', use_container_width=True, on_click=check_flavor_and_show_analysis)
    
    if st.session_state.get('show_flavor_warning', False):
        st.warning('⚠️ 请先选择口味后再进行达成分析')

    with col10:
        st.markdown('<div style="margin-top: 25px;"></div>', unsafe_allow_html=True)
        st.button('🗑️ 清除筛选', key='btn_clear_filters', use_container_width=True, on_click=lambda: st.session_state.update({'clear_filters': True}))

    st.session_state['current_analysis_project'] = project
    st.session_state['current_analysis_product30'] = product30
    st.session_state['current_analysis_product20'] = product20

    filtered_df = df.copy()

    if region != '全部':
        filtered_df = filtered_df[filtered_df['营业部'].isin(REGION_DEPT_MAP[region])]

    if dept != '全部':
        filtered_df = filtered_df[filtered_df['营业部'] == dept]

    if project != '全部':
        filtered_df = filtered_df[filtered_df['口味'].isin(project_map[project])]

    if product30 != '全部':
        filtered_df = filtered_df[filtered_df['口味'].isin(product30_map[product30])]

    if product20 != '全部':
        filtered_df = filtered_df[filtered_df['口味'].isin(product20_map[product20])]

    if capacity != '全部':
        filtered_df = filtered_df[filtered_df['容量'] == capacity]

    if flavor != '全部':
        filtered_df = filtered_df[filtered_df['口味'] == flavor]

    total_demand = filtered_df['需求量'].sum()
    total_budget = filtered_df['预算销量'].sum()
    total_last_year = filtered_df['去年同期销量'].sum()
    monthly_order = filtered_df['月累排单'].sum()
    avg_budget_achievement = (monthly_order / total_budget * 100) if total_budget > 0 else 0
    avg_growth = ((total_demand - total_last_year) / total_last_year * 100) if total_last_year > 0 else 0
    monthly_order_achievement = (monthly_order / total_demand * 100) if total_demand > 0 else 0

    growth_color = '#ef4444' if avg_growth < 0 else '#1e40af'

    growth_card_class = 'metric-card-red' if avg_growth < 0 else 'metric-card-green'
    growth_value_class = 'metric-value-red' if avg_growth < 0 else 'metric-value-green'
    growth_trend_icon = '↓' if avg_growth < 0 else '↑'
    growth_trend_color = '#dc2626' if avg_growth < 0 else '#059669'
    
    st.markdown(f"""
        <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 20px; margin-bottom: 24px;'>
            <div class='metric-card-blue'>
                <div class='metric-value-blue'>{int(total_demand):,}</div>
                <div class='metric-label'>总需求量</div>
            </div>
            <div class='metric-card-blue'>
                <div class='metric-value-blue'>{int(total_budget):,}</div>
                <div class='metric-label'>总预算销量</div>
            </div>
            <div class='metric-card-blue'>
                <div class='metric-value-blue'>{int(monthly_order):,}</div>
                <div class='metric-label'>月累排单</div>
            </div>
            <div class='metric-card-orange'>
                <div class='metric-value-orange'>{avg_budget_achievement:.1f}%</div>
                <div class='metric-label'>预算达成率</div>
            </div>
            <div class='{growth_card_class}'>
                <div class='{growth_value_class}'>{avg_growth:.1f}%</div>
                <div class='metric-label'>较同期成长</div>
                <div class='metric-trend' style='color: {growth_trend_color};'>
                    <span style='margin-right: 4px;'>{growth_trend_icon}</span>
                    {growth_trend_color == '#dc2626' and '同比下降' or '同比增长'}
                </div>
            </div>
            <div class='metric-card-orange'>
                <div class='metric-value-orange'>{monthly_order_achievement:.1f}%</div>
                <div class='metric-label'>月累排单达成率</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    col_dept, col_right = st.columns([2, 1.5], gap='medium')

    with col_dept:
        dept_filtered_df = filtered_df.copy()
        
        selected_cap = st.session_state.get('selected_capacity_for_dept')
        if selected_cap:
            dept_filtered_df = dept_filtered_df[dept_filtered_df['容量'].astype(str) == str(selected_cap)]
        
        dept_df = dept_filtered_df.groupby('营业部').agg({
            '需求量': 'sum',
            '去年同期销量': 'sum',
            '预算销量': 'sum',
            '月累排单': 'sum',
            '月累销量': 'sum'
        }).reset_index()
        dept_df = dept_df.sort_values('需求量', ascending=False)
        dept_df['排单需求达成率'] = dept_df.apply(lambda row: 0 if (row['需求量'] == 0 or row['月累排单'] == 0) else (row['月累排单'] / row['需求量'] * 100), axis=1)
        dept_df['排单预算达成率'] = dept_df.apply(lambda row: 0 if (row['预算销量'] == 0 or row['月累排单'] == 0) else (row['月累排单'] / row['预算销量'] * 100), axis=1)
        dept_df['月累排单较同期'] = dept_df.apply(lambda row: 0 if row['去年同期销量'] == 0 else ((row['月累排单'] - row['去年同期销量']) / row['去年同期销量'] * 100), axis=1)

        st.markdown("""
            <style>
            .focus-report-btn {
                background: linear-gradient(135deg, #1a73e8 0%, #4285f4 100%);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 500;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 8px;
                transition: all 0.2s ease;
                box-shadow: 0 2px 8px rgba(66, 133, 244, 0.3);
            }
            .focus-report-btn:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(66, 133, 244, 0.4);
            }
            .modal-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.5);
                display: none;
                justify-content: center;
                align-items: center;
                z-index: 10000;
            }
            .modal-content {
                background: white;
                border-radius: 16px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                max-width: 700px;
                width: 90%;
                max-height: 80vh;
                overflow-y: auto;
                position: relative;
            }
            .modal-header {
                padding: 20px 24px;
                background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
                color: white;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .modal-title {
                font-size: 20px;
                font-weight: 600;
                color: #1e293b;
            }
            .modal-close {
                background: none;
                border: none;
                font-size: 24px;
                cursor: pointer;
                color: #94a3b8;
                padding: 0;
                line-height: 1;
            }
            .modal-body {
                padding: 24px;
            }
            .modal-section {
                margin-bottom: 32px;
            }
            .modal-section-title {
                font-size: 16px;
                font-weight: 600;
                color: #334155;
                margin-bottom: 16px;
                padding-left: 12px;
                border-left: 4px solid #3b82f6;
            }
            .modal-list {
                background: #f8fafc;
                border-radius: 8px;
                padding: 12px;
            }
            .modal-item {
                padding: 12px;
                border-bottom: 1px solid #e2e8f0;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .modal-item:last-child {
                border-bottom: none;
            }
            .modal-item-name {
                font-weight: 500;
                color: #374151;
            }
            .modal-item-value {
                font-weight: 600;
                color: #1e293b;
            }
            .modal-item-warning {
                color: #ef4444;
            }
            .modal-alert {
                background: #fff3cd;
                border: 1px solid #ffeeba;
                border-radius: 8px;
                padding: 16px;
                color: #856404;
            }
            </style>
        """, unsafe_allow_html=True)

        avg_demand_rate = dept_df['排单需求达成率'].mean()
        avg_budget_rate = dept_df['排单预算达成率'].mean()
        
        if pd.isna(avg_demand_rate):
            avg_demand_rate = 0
        if pd.isna(avg_budget_rate):
            avg_budget_rate = 0
        
        low_demand_depts = dept_df[dept_df['排单需求达成率'] < avg_demand_rate]
        low_budget_depts = dept_df[dept_df['排单预算达成率'] < avg_budget_rate]
        
        total_demand = filtered_df['需求量'].sum()
        total_order = filtered_df['月累排单'].sum()
        
        # 创建表格HTML（不包含按钮）
        table_html = "<div class='section-card' style='margin-top: -20px;'>"
        table_html += "<div class='section-title'>需求分析（营业部别）</div>"
        table_html += "<div style='overflow-x: auto; height: 595px; overflow-y: auto; position: relative;'>"
        table_html += "<table class='custom-table'>"
        table_html += "<thead><tr>"
        table_html += "<th>营业部</th><th>需求量</th><th>预算<br>销量</th><th>同期<br>销量</th><th>月累排单</th><th>月累<br>销量</th><th>排单需求<br>达成率</th><th>排单预算<br>达成率</th><th>月累排单<br>较同期</th>"
        table_html += "</tr></thead><tbody>"

        def get_rate_style(rate):
            if rate < 60:
                return {'bg': '#ffe6e6', 'text': '#c00000', 'weight': 'normal', 'italic': False}
            elif 60 <= rate < 80:
                return {'bg': '#fff4e6', 'text': '#e67e22', 'weight': 'normal', 'italic': False}
            elif 80 <= rate < 100:
                return {'bg': '#e6f7e6', 'text': '#16a34a', 'weight': 'normal', 'italic': False}
            else:
                return {'bg': '#d0e8d0', 'text': '#1e5a1e', 'weight': 'bold', 'italic': rate > 120}
        
        for _, row in dept_df.iterrows():
            dr_rate = row['排单需求达成率']
            db_rate = row['排单预算达成率']
            
            dr_style = get_rate_style(dr_rate)
            db_style = get_rate_style(db_rate)
            
            dr_label = f"{dr_rate:.1f}%"
            db_label = f"{db_rate:.1f}%"
            
            if dr_style['italic']:
                dr_label = f"<em>{dr_label}*</em>"
            if db_style['italic']:
                db_label = f"<em>{db_label}*</em>"
            
            dr_bar_width = min(dr_rate, 100)
            dr_bar_color = '#1e5a1e' if dr_rate >= 100 else '#86efac' if dr_rate >= 80 else '#e67e22' if dr_rate >= 60 else '#c00000'
            
            db_bar_width = min(db_rate, 100)
            db_bar_color = '#1e5a1e' if db_rate >= 100 else '#86efac' if db_rate >= 80 else '#e67e22' if db_rate >= 60 else '#c00000'
            
            selected_dept = st.session_state.get('selected_dept', '')
            row_class = "selected-row" if row['营业部'] == selected_dept else ""
            
            table_html += f"<tr class='clickable-row {row_class}' style='cursor: pointer;' onclick=\"document.getElementById('select-dept-{row['营业部'].replace(' ', '-')}').click()\">"
            table_html += f"<td>{row['营业部']}</td>"
            table_html += f"<td>{row['需求量']:.2f}</td>"
            table_html += f"<td>{row['预算销量']:.2f}</td>"
            table_html += f"<td>{row['去年同期销量']:.2f}</td>"
            table_html += f"<td>{row['月累排单']:.2f}</td>"
            table_html += f"<td>{row['月累销量']:.2f}</td>"
            table_html += f"<td style='padding: 8px;'>"
            table_html += f"<div style='font-weight: {dr_style['weight']}; color: {dr_style['text']}; margin-bottom: 4px;'>{dr_label}</div>"
            table_html += f"<div style='width: 100%; height: 8px; background-color: #e5e7eb; border-radius: 4px; overflow: hidden;'>"
            table_html += f"<div style='width: {dr_bar_width}%; height: 100%; background-color: {dr_bar_color}; border-radius: 4px; transition: width 0.3s ease;'></div>"
            table_html += "</div></td>"
            table_html += f"<td style='padding: 8px;'>"
            table_html += f"<div style='font-weight: {db_style['weight']}; color: {db_style['text']}; margin-bottom: 4px;'>{db_label}</div>"
            table_html += f"<div style='width: 100%; height: 8px; background-color: #e5e7eb; border-radius: 4px; overflow: hidden;'>"
            table_html += f"<div style='width: {db_bar_width}%; height: 100%; background-color: {db_bar_color}; border-radius: 4px; transition: width 0.3s ease;'></div>"
            table_html += "</div></td>"
            
            growth_rate = row['月累排单较同期']
            growth_label = f"{growth_rate:+.1f}%"
            growth_color = '#16a34a' if growth_rate >= 0 else '#dc2626'
            
            table_html += f"<td style='padding: 8px; text-align: center;'>"
            table_html += f"<div style='font-weight: 600; color: {growth_color};'>{growth_label}</div>"
            table_html += f"<div style='font-size: 12px; color: #64748b;'>{'成长' if growth_rate >= 0 else '衰退'}</div>"
            table_html += "</td>"
            
            table_html += "</tr>"

        table_html += "</tbody></table></div></div>"
        st.markdown(table_html, unsafe_allow_html=True)
        
        # 模态框显示逻辑（使用Streamlit状态控制）
        if st.session_state.show_focus_report:
            # 使用简单的模态框样式
            st.markdown("""
            <style>
                .simple-modal-overlay {
                    position: fixed !important;
                    top: 0 !important;
                    left: 0 !important;
                    width: 100% !important;
                    height: 100% !important;
                    background-color: rgba(0,0,0,0.5) !important;
                    display: flex !important;
                    justify-content: center !important;
                    align-items: center !important;
                    z-index: 9999 !important;
                }
                .simple-modal-content {
                    background: white !important;
                    border-radius: 12px !important;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3) !important;
                    max-width: 800px !important;
                    width: 90% !important;
                    max-height: 80vh !important;
                    overflow-y: auto !important;
                    position: relative !important;
                }
            </style>
            """, unsafe_allow_html=True)
            
            total_depts = len(dept_df)
            abnormal_count = sum(1 for _, row in dept_df.iterrows() if (row['排单需求达成率'] > 0 and row['排单需求达成率'] < avg_demand_rate) or (row['排单预算达成率'] > 0 and row['排单预算达成率'] < avg_budget_rate))
            
            # 直接显示模态框内容
            st.markdown("""
            <div class="simple-modal-overlay">
                <div class="simple-modal-content">
                    <div style="padding: 20px 24px; background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); color: white; display: flex; justify-content: space-between; align-items: center; border-radius: 12px 12px 0 0;">
                        <div>
                            <div style="font-size: 18px; font-weight: 600;">🔍 智能异常排查报告</div>
                            <div style="font-size: 12px; opacity: 0.8; margin-top: 4px;">当前筛选覆盖 """ + str(total_depts) + """ 个营业部，发现 """ + str(abnormal_count) + """ 个异常营业部</div>
                        </div>
                    </div>
                    <div style="padding: 24px;">
                        <div style="font-size: 16px; font-weight: 600; color: #334155; margin-bottom: 16px; padding-left: 12px; border-left: 4px solid #ef4444;">异常营业部汇总表</div>
                        <table style="width:100%;border-collapse:collapse;margin-top:16px;border-radius:8px;overflow:hidden;">
                            <thead>
                                <tr style="background-color:#f8fafc;">
                                    <th style="padding:12px 14px;text-align:left;font-size:11px;font-weight:600;color:#64748b;border-bottom:2px solid #e2e8f0;">营业部名称</th>
                                    <th style="padding:12px 14px;text-align:left;font-size:11px;font-weight:600;color:#64748b;border-bottom:2px solid #e2e8f0;">排单需求达成率(%)</th>
                                    <th style="padding:12px 14px;text-align:left;font-size:11px;font-weight:600;color:#64748b;border-bottom:2px solid #e2e8f0;">需求达成率vs平均</th>
                                    <th style="padding:12px 14px;text-align:left;font-size:11px;font-weight:600;color:#64748b;border-bottom:2px solid #e2e8f0;">排单预算达成率(%)</th>
                                    <th style="padding:12px 14px;text-align:left;font-size:11px;font-weight:600;color:#64748b;border-bottom:2px solid #e2e8f0;">预算达成率vs平均</th>
                                    <th style="padding:12px 14px;text-align:left;font-size:11px;font-weight:600;color:#64748b;border-bottom:2px solid #e2e8f0;">异常类型</th>
                                </tr>
                            </thead>
                            <tbody>
            """, unsafe_allow_html=True)
            
            # 表格内容
            has_abnormal = False
            abnormal_depts = []
            
            for _, row in dept_df.iterrows():
                demand_diff = row['排单需求达成率'] - avg_demand_rate
                budget_diff = row['排单预算达成率'] - avg_budget_rate
                demand_below = row['排单需求达成率'] > 0 and row['排单需求达成率'] < avg_demand_rate
                budget_below = row['排单预算达成率'] > 0 and row['排单预算达成率'] < avg_budget_rate
                
                if demand_below or budget_below:
                    has_abnormal = True
                    abnormal_depts.append({
                        '营业部': row['营业部'],
                        '排单需求达成率': row['排单需求达成率'],
                        '排单预算达成率': row['排单预算达成率'],
                        'demand_diff': demand_diff,
                        'budget_diff': budget_diff,
                        'demand_below': demand_below,
                        'budget_below': budget_below
                    })
            
            for dept_data in abnormal_depts:
                    demand_below = dept_data['demand_below']
                    budget_below = dept_data['budget_below']
                    demand_diff = dept_data['demand_diff']
                    budget_diff = dept_data['budget_diff']
                    
                    abnormal_type = '两者均低' if (demand_below and budget_below) else ('需求达成率低' if demand_below else '预算达成率低')
                    demand_color = '#ef4444' if demand_below else '#374151'
                    budget_color = '#ef4444' if budget_below else '#374151'
                    demand_arrow = '↓' if demand_below else ''
                    budget_arrow = '↓' if budget_below else ''
                    type_color = '#ef4444' if abnormal_type == '两者均低' else ('#f59e0b' if abnormal_type == '需求达成率低' else '#3b82f6')
                    
                    st.markdown(f"""
                    <tr style="background-color:#fefefe;">
                        <td style="padding:12px 14px;font-size:12px;color:#374151;border-bottom:1px solid #f1f5f9;font-weight:500;">{dept_data['营业部']}</td>
                        <td style="padding:12px 14px;font-size:12px;color:{demand_color};border-bottom:1px solid #f1f5f9;font-weight:{600 if demand_below else 400};">{dept_data['排单需求达成率']:.2f}</td>
                        <td style="padding:12px 14px;font-size:12px;color:{demand_color};border-bottom:1px solid #f1f5f9;font-weight:{600 if demand_below else 400};">{demand_arrow} {abs(demand_diff):.2f}%</td>
                        <td style="padding:12px 14px;font-size:12px;color:{budsetColor};border-bottom:1px solid #f1f5f9;font-weight:{600 if budget_below else 400};">{dept_data['排单预算达成率']:.2f}</td>
                        <td style="padding:12px 14px;font-size:12px;color:{budsetColor};border-bottom:1px solid #f1f5f9;font-weight:{600 if budget_below else 400};">{budget_arrow} {abs(budget_diff):.2f}%</td>
                        <td style="padding:12px 14px;font-size:12px;color:{type_color};border-bottom:1px solid #f1f5f9;font-weight:600;">{abnormal_type}</td>
                    </tr>
                    """, unsafe_allow_html=True)
            
            if not has_abnormal:
                st.markdown('<tr><td colspan="6" style="padding:20px;text-align:center;color:#10b981;font-weight:500;">✓ 未发现异常营业部</td></tr>', unsafe_allow_html=True)
            
            st.markdown("""
                            </tbody>
                        </table>
                        
                        <div style="font-size: 16px; font-weight: 600; color: #334155; margin-bottom: 16px; padding-left: 12px; border-left: 4px solid #f59e0b; margin-top: 24px;">详细差异分析</div>
            """, unsafe_allow_html=True)
            
            # 详细差异分析
            for _, row in dept_df.iterrows():
                demand_below = row['排单需求达成率'] > 0 and row['排单需求达成率'] < avg_demand_rate
                budget_below = row['排单预算达成率'] > 0 and row['排单预算达成率'] < avg_budget_rate
                
                if demand_below or budget_below:
                    dept_name = row['营业部']
                    
                    dept_filtered = filtered_df[filtered_df['营业部'] == dept_name]
                    
                    flavor_diff = {}
                    flavors = dept_filtered['口味'].unique()
                    for flavor in flavors:
                        flavor_data = dept_filtered[dept_filtered['口味'] == flavor]
                        demand_sum = flavor_data['需求量'].sum()
                        order_sum = flavor_data['月累排单'].sum()
                        if demand_sum > 0:
                            diff = (order_sum - demand_sum) / demand_sum * 100
                            flavor_diff[flavor] = diff
                    
                    max_flavor = max(flavor_diff, key=lambda k: abs(flavor_diff[k])) if flavor_diff else ''
                    
                    capacity_diff = {}
                    capacities = dept_filtered['容量'].unique()
                    for cap in capacities:
                        cap_data = dept_filtered[dept_filtered['容量'] == cap]
                        demand_sum = cap_data['需求量'].sum()
                        order_sum = cap_data['月累排单'].sum()
                        capacity_diff[str(cap)] = order_sum - demand_sum
                    
                    max_capacity = max(capacity_diff, key=lambda k: abs(capacity_diff[k])) if capacity_diff else ''
                    
                    flavor_html = ''
                    for flavor, diff in flavor_diff.items():
                        is_max = flavor == max_flavor
                        warning = '⚠️' if abs(diff) > 10 else ''
                        diff_color = '#ef4444' if diff < 0 else '#10b981'
                        sign = '+' if diff > 0 else ''
                        flavor_html += f"""
                        <div style="padding: 8px 12px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #e2e8f0;">
                            <span style="font-size: 12px; color: #374151;">{flavor}{warning}</span>
                            <span style="font-size: 12px; color: {diff_color}; font-weight: 500;">{sign}{diff:.2f}%</span>
                        </div>
                        """
                    
                    capacity_html = ''
                    for cap, diff in capacity_diff.items():
                        is_max = cap == max_capacity
                        warning = '❗' if abs(diff) > 200 else ''
                        diff_color = '#ef4444' if diff < 0 else '#10b981'
                        sign = '+' if diff > 0 else ''
                        capacity_html += f"""
                        <div style="padding: 8px 12px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #e2e8f0;">
                            <span style="font-size: 12px; color: #374151;">{cap}ml{warning}</span>
                            <span style="font-size: 12px; color: {diff_color}; font-weight: 500;">{sign}{diff:.2f}</span>
                        </div>
                        """
                    
                    st.markdown(f"""
                        <div style="border: 1px solid #e2e8f0; border-radius: 8px; margin-top: 16px; overflow:hidden;">
                            <div style="background: #f8fafc; padding: 12px 16px;">
                                <div style="font-size: 14px; font-weight: 600; color: #1e293b; display: flex; align-items: center;">
                                    <span style="width: 4px; height: 14px; background: #4f46e5; border-radius: 2px; margin-right: 10px;"></span>
                                    {dept_name} - 详细差异分析
                                </div>
                            </div>
                            <div style="padding: 16px; display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                                <div>
                                    <div style="font-size: 12px; font-weight: 600; color: #64748b; margin-bottom: 8px;">口味差异分析</div>
                                    <div style="background: #f8fafc; border-radius: 6px; padding: 4px;">{flavor_html}</div>
                                </div>
                                <div>
                                    <div style="font-size: 12px; font-weight: 600; color: #64748b; margin-bottom: 8px;">容量差异分析</div>
                                    <div style="background: #f8fafc; border-radius: 6px; padding: 4px;">{capacity_html}</div>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("""
                        <div style="font-size: 16px; font-weight: 600; color: #334155; margin-bottom: 16px; padding-left: 12px; border-left: 4px solid #f59e0b; margin-top: 24px;">容量别供需情况</div>
                        <div style="background: #fff3cd; border: 1px solid #ffeeba; border-radius: 8px; padding: 14px; color: #856404; font-size: 13px;">
                            ⚠️ 容量别供需情况：需求""" + f"{total_demand:.2f}" + """ vs 排单""" + f"{total_order:.2f}" + """
                        </div>
                    </div>
                    
                    <div style="padding: 16px 24px; border-top: 1px solid #e2e8f0; text-align: center;">
                        <button onclick="window.location.reload();" style="background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); color: white; border: none; padding: 10px 30px; border-radius: 8px; font-size: 13px; font-weight: 500; cursor: pointer; transition: all 0.2s ease; box-shadow: 0 2px 8px rgba(79,70,229,0.3);">关闭</button>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        card_container = st.container(border=True)
        with card_container:
            st.markdown("<div class='section-title'>需求与排单对比（口味别）</div>", unsafe_allow_html=True)
            monthly_order_flavor_df = filtered_df.groupby('口味').agg({
                '月累排单': 'sum',
                '需求量': 'sum'
            }).reset_index()
            monthly_order_flavor_df = monthly_order_flavor_df.sort_values('需求量', ascending=False)
            
            import plotly.graph_objects as go
            fig_monthly_order = go.Figure()
            fig_monthly_order.add_trace(go.Bar(
                y=monthly_order_flavor_df['口味'],
                x=monthly_order_flavor_df['需求量'],
                name='需求量',
                orientation='h',
                marker_color='#1e40af',
                text=monthly_order_flavor_df['需求量'].apply(lambda x: f'{x:.2f}'),
                textposition='outside',
                textfont=dict(
                    size=13,
                    weight='bold',
                    color='#1e40af'
                ),
                insidetextanchor='end'
            ))
            fig_monthly_order.add_trace(go.Bar(
                y=monthly_order_flavor_df['口味'],
                x=monthly_order_flavor_df['月累排单'],
                name='月累排单',
                orientation='h',
                marker_color='#60a5fa',
                text=monthly_order_flavor_df['月累排单'].apply(lambda x: f'{x:.2f}'),
                textposition='outside',
                textfont=dict(
                    size=13,
                    weight='bold',
                    color='#1e40af'
                ),
                insidetextanchor='end'
            ))
            max_value = max(monthly_order_flavor_df['需求量'].max(), monthly_order_flavor_df['月累排单'].max())
            fig_monthly_order.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                yaxis=dict(autorange="reversed", showgrid=False, tickfont=dict(size=10)),
                xaxis=dict(showgrid=True, gridcolor='#e2e8f0', tickfont=dict(size=10), range=[0, max_value * 1.2]),
                margin=dict(l=10, r=60, t=10, b=10),
                barmode='group',
                bargap=0.3,
                bargroupgap=0.2,
                height=220,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_monthly_order, use_container_width=True)
        
        card_container = st.container(border=True)
        with card_container:
            st.markdown("<div class='section-title'>需求与排单（容量别）</div>", unsafe_allow_html=True)
            if '容量' in filtered_df.columns:
                valid_df = filtered_df[(filtered_df['需求量'] > 0) | (filtered_df['月累排单'] > 0)]
                capacity_df = valid_df.groupby('容量').agg({
                    '月累排单': 'sum',
                    '需求量': 'sum'
                }).reset_index()
                
                capacity_df = capacity_df[(capacity_df['需求量'] > 0) | (capacity_df['月累排单'] > 0)]
                capacity_df = capacity_df.sort_values('需求量', ascending=False)
                
                capacity_df['差异量'] = capacity_df['月累排单'] - capacity_df['需求量']
                capacity_df['差异百分比'] = (capacity_df['差异量'] / capacity_df['需求量'] * 100).apply(lambda x: f'{x:+.2f}%')
                
                import plotly.graph_objects as go
                fig_capacity = go.Figure()
                fig_capacity.add_trace(go.Scatter(
                    x=capacity_df['容量'],
                    y=capacity_df['需求量'],
                    mode='lines+markers+text',
                    name='需求量',
                    line=dict(color='#1e40af', width=3, dash='solid'),
                    marker=dict(color='#1e40af', size=8, symbol='circle', line=dict(width=2, color='#ffffff')),
                    text=capacity_df['需求量'].apply(lambda x: f'{x:.2f}'),
                    textposition='top center',
                    textfont=dict(color='#1e40af', size=14, weight='bold'),
                    customdata=capacity_df['容量'],
                    hovertemplate='<b>容量:</b> %{customdata}<br><b>需求量:</b> %{y:.2f}<extra></extra>'
                ))
                fig_capacity.add_trace(go.Scatter(
                    x=capacity_df['容量'],
                    y=capacity_df['月累排单'],
                    mode='lines+markers+text',
                    name='月累排单',
                    line=dict(color='#ea580c', width=3, dash='dash'),
                    marker=dict(color='#ea580c', size=8, symbol='square', line=dict(width=2, color='#ffffff')),
                    text=capacity_df['月累排单'].apply(lambda x: f'{x:.2f}'),
                    textposition='bottom center',
                    textfont=dict(color='#ea580c', size=14, weight='bold'),
                    customdata=capacity_df['容量'],
                    hovertemplate='<b>容量:</b> %{customdata}<br><b>月累排单:</b> %{y:.2f}<extra></extra>'
                ))
                max_value = max(capacity_df['需求量'].max(), capacity_df['月累排单'].max())
                offset = max_value * 0.25 if max_value > 0 else 12
                
                for _, row in capacity_df.iterrows():
                    diff_color = '#059669' if row['差异量'] > 0 else '#dc2626'
                    diff_text = f'{"+" if row["差异量"] > 0 else ""}{row["差异量"]:.2f}'
                    fig_capacity.add_trace(go.Scatter(
                        x=[row['容量']],
                        y=[max(row['需求量'], row['月累排单']) + offset],
                        mode='text',
                        name='差异量',
                        text=[diff_text],
                        textposition='bottom center',
                        textfont=dict(color=diff_color, size=14, weight='bold'),
                        showlegend=False,
                        customdata=[row['容量']]
                    ))
                fig_capacity.update_layout(
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    yaxis=dict(showgrid=True, gridcolor='#e2e8f0', tickfont=dict(size=10), title='量'),
                    xaxis=dict(showgrid=False, tickfont=dict(size=10), type='category', categoryorder='array', categoryarray=capacity_df['容量'].tolist()),
                    margin=dict(l=40, r=40, t=40, b=40),
                    height=260,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                
                st.plotly_chart(fig_capacity, use_container_width=True, key='capacity_chart')
                
                st.markdown("""
                    <style>
                    #capacity_filter_wrapper {
                        margin-top: -70px !important;
                        margin-bottom: 0 !important;
                        display: flex !important;
                        align-items: center !important;
                        gap: 8px !important;
                        width: fit-content !important;
                    }
                    #capacity_filter_wrapper .stSelectbox {
                        width: 60px !important;
                        margin: 0 !important;
                        padding: 0 !important;
                    }
                    #capacity_filter_wrapper .stSelectbox > div {
                        width: 60px !important;
                        min-width: 60px !important;
                        max-width: 60px !important;
                        margin: 0 !important;
                        padding: 0 !important;
                    }
                    #capacity_filter_wrapper .stSelectbox [data-baseweb="select"] {
                        width: 60px !important;
                        min-width: 60px !important;
                        max-width: 60px !important;
                    }
                    #capacity_filter_wrapper .stSelectbox [data-baseweb="select"] > div {
                        height: 30px !important;
                        width: 60px !important;
                        min-width: 60px !important;
                        max-width: 60px !important;
                        padding: 0 !important;
                    }
                    </style>
                """, unsafe_allow_html=True)
                
                capacity_list = list(capacity_df['容量'].astype(str))
                current_cap = st.session_state.get('selected_capacity_for_dept')
                if current_cap and str(current_cap) in capacity_list:
                    select_index = capacity_list.index(str(current_cap)) + 1
                else:
                    select_index = 0
                
                st.markdown('<div id="capacity_filter_wrapper">', unsafe_allow_html=True)
                selected_cap = st.selectbox(
                    "选择容量",
                    options=['全部'] + capacity_list,
                    index=select_index,
                    key='capacity_select',
                    label_visibility='hidden'
                )
                st.markdown("</div>", unsafe_allow_html=True)
                
                if selected_cap != '全部':
                    if st.session_state.get('selected_capacity_for_dept') != selected_cap:
                        st.session_state['selected_capacity_for_dept'] = selected_cap
                        st.rerun()
        
            else:
                st.markdown("<div style='text-align: center; color: #9ca3af; padding-top: 80px;'>数据中不含容量列</div>", unsafe_allow_html=True)
            
            if 'selected_capacity' in st.session_state and st.session_state['selected_capacity']:
                info_col, btn_col = st.columns([3, 1])
                with info_col:
                    st.markdown(f"""
                        <div style='padding: 12px; background: #eff6ff; border-radius: 8px; margin-top: 12px;'>
                            <span style='color: #1e40af; font-weight: 500;'>已选择容量: <strong>{st.session_state['selected_capacity']}</strong></span>
                        </div>
                    """, unsafe_allow_html=True)
                with btn_col:
                    if st.button("清除筛选", key='clear_capacity', use_container_width=True):
                        st.session_state['selected_capacity'] = None
                        st.rerun()
            else:
                pass

    col_a, col_b = st.columns(2)

    with col_a:
        capacity_df = filtered_df.groupby('容量').agg({
            '需求量': 'sum',
            '月累排单': 'sum',
            '去年同期销量': 'sum',
            '预算销量': 'sum'
        }).reset_index()
        capacity_df = capacity_df.sort_values('需求量', ascending=False)
        capacity_df['预算达成'] = capacity_df.apply(lambda row: 0 if (row['预算销量'] == 0 or row['需求量'] == 0) else (row['需求量'] / row['预算销量'] * 100), axis=1)
        capacity_df['较同期成长'] = capacity_df.apply(lambda row: 0 if (row['去年同期销量'] == 0 or row['需求量'] == 0) else ((row['需求量'] - row['去年同期销量']) / row['去年同期销量'] * 100), axis=1)

        table_html = "<div class='section-card'>"
        table_html += "<div class='section-title'>需求分析（容量别）</div>"
        table_html += "<div style='overflow-x: auto; max-height: 400px; overflow-y: auto;'>"
        table_html += "<table class='custom-table'>"
        table_html += "<thead><tr>"
        table_html += "<th>容量</th><th>需求量</th><th>预算<br>销量</th><th>同期<br>销量</th><th>预算<br>达成</th><th>较同期<br>成长</th><th>月累排单</th><th>差量</th><th>差量率</th>"
        table_html += "</tr></thead><tbody>"

        for _, row in capacity_df.iterrows():
            budget_rate = row['预算达成']
            growth_rate = row['较同期成长']
            
            diff_amount = row['月累排单'] - row['需求量']
            diff_rate = (diff_amount / row['需求量'] * 100) if row['需求量'] > 0 else float('nan')
            
            budget_display = f"{budget_rate:.2f}%" if (pd.notna(budget_rate) and abs(budget_rate) != float('inf')) else '--'
            growth_display = f"{growth_rate:.2f}%" if (pd.notna(growth_rate) and abs(growth_rate) != float('inf')) else '--'
            diff_rate_display = f"{diff_rate:.2f}%" if (pd.notna(diff_rate) and abs(diff_rate) != float('inf')) else '--'
            
            growth_style = "color: #ef4444; font-weight: bold;" if (growth_rate < 0 and pd.notna(growth_rate)) else ""
            
            diff_color = '#dc2626' if (diff_amount < 0 and pd.notna(diff_amount)) else '#059669'
            diff_style = f"color: {diff_color}; font-weight: bold;"
            
            table_html += "<tr>"
            table_html += f"<td>{row['容量']}</td>"
            table_html += f"<td>{row['需求量']:.2f}</td>"
            table_html += f"<td>{row['预算销量']:.2f}</td>"
            table_html += f"<td>{row['去年同期销量']:.2f}</td>"
            table_html += f"<td>{budget_display}</td>"
            table_html += f"<td style='{growth_style}'>{growth_display}</td>"
            table_html += f"<td>{row['月累排单']:.2f}</td>"
            table_html += f"<td style='{diff_style}'>{diff_amount:.2f}</td>"
            table_html += f"<td style='{diff_style}'>{diff_rate_display}</td>"
            table_html += "</tr>"

        table_html += "</tbody></table></div></div>"
        st.markdown(table_html, unsafe_allow_html=True)

    with col_b:
        flavor_df = filtered_df.groupby('口味').agg({
            '需求量': 'sum',
            '月累排单': 'sum',
            '去年同期销量': 'sum',
            '预算销量': 'sum'
        }).reset_index()
        flavor_df = flavor_df.sort_values('需求量', ascending=False)
        flavor_df['预算达成'] = flavor_df.apply(lambda row: 0 if (row['预算销量'] == 0 or row['需求量'] == 0) else (row['需求量'] / row['预算销量'] * 100), axis=1)
        flavor_df['较同期成长'] = flavor_df.apply(lambda row: 0 if row['去年同期销量'] == 0 else ((row['需求量'] - row['去年同期销量']) / row['去年同期销量'] * 100), axis=1)
        flavor_df['差量'] = flavor_df.apply(lambda row: row['月累排单'] - row['需求量'], axis=1)
        flavor_df['差量率'] = flavor_df.apply(lambda row: 0 if row['需求量'] == 0 else ((row['月累排单'] - row['需求量']) / row['需求量'] * 100), axis=1)

        table_html = "<div class='section-card'>"
        table_html += "<div class='section-title'>需求分析（口味别）</div>"
        table_html += "<div style='overflow-x: auto; max-height: 400px; overflow-y: auto;'>"
        table_html += "<table class='custom-table'>"
        table_html += "<thead><tr>"
        table_html += "<th>口味</th><th>需求量</th><th>预算<br>销量</th><th>同期<br>销量</th><th>预算<br>达成</th><th>较同期<br>成长</th><th>月累排单</th><th>差量</th><th>差量率</th>"
        table_html += "</tr></thead><tbody>"

        for _, row in flavor_df.iterrows():
            budget_rate = row['预算达成']
            growth_rate = row['较同期成长']
            diff_rate = row['差量率']
            
            budget_display = f"{budget_rate:.2f}%" if (pd.notna(budget_rate) and abs(budget_rate) != float('inf')) else '--'
            growth_display = f"{growth_rate:.2f}%" if (pd.notna(growth_rate) and abs(growth_rate) != float('inf')) else '--'
            diff_rate_display = f"{diff_rate:.2f}%" if (pd.notna(diff_rate) and abs(diff_rate) != float('inf')) else '--'
            
            growth_style = "color: #ef4444; font-weight: bold;" if (growth_rate < 0 and pd.notna(growth_rate)) else ""
            
            diff_color = '#dc2626' if (row['差量'] < 0 and pd.notna(row['差量'])) else '#059669'
            diff_style = f"color: {diff_color}; font-weight: bold;"
            
            table_html += "<tr>"
            table_html += f"<td>{row['口味']}</td>"
            table_html += f"<td>{row['需求量']:.2f}</td>"
            table_html += f"<td>{row['预算销量']:.2f}</td>"
            table_html += f"<td>{row['去年同期销量']:.2f}</td>"
            table_html += f"<td>{budget_display}</td>"
            table_html += f"<td style='{growth_style}'>{growth_display}</td>"
            table_html += f"<td>{row['月累排单']:.2f}</td>"
            table_html += f"<td style='{diff_style}'>{row['差量']:.2f}</td>"
            table_html += f"<td style='{diff_style}'>{diff_rate_display}</td>"
            table_html += "</tr>"

        table_html += "</tbody></table></div></div>"
        st.markdown(table_html, unsafe_allow_html=True)

    card_container = st.container(border=True)
    with card_container:
        st.markdown("<div class='section-title'>📊 贡献度分析（帕累托）</div>", unsafe_allow_html=True)
        
        pareto_df = filtered_df.groupby('口味').agg({
            '需求量': 'sum'
        }).reset_index()
        pareto_df = pareto_df.sort_values('需求量', ascending=False)
        pareto_df['累计需求量'] = pareto_df['需求量'].cumsum()
        pareto_df['累计百分比'] = (pareto_df['累计需求量'] / pareto_df['需求量'].sum() * 100).round(1)
        pareto_df['排名'] = range(1, len(pareto_df) + 1)
        
        fig_pareto = go.Figure()
        
        fig_pareto.add_trace(go.Bar(
            x=pareto_df['口味'],
            y=pareto_df['需求量'],
            name='需求量',
            marker_color='#3b82f6',
            yaxis='y1'
        ))
        
        fig_pareto.add_trace(go.Scatter(
            x=pareto_df['口味'],
            y=pareto_df['累计百分比'],
            name='累计占比',
            marker_color='#f59e0b',
            yaxis='y2',
            mode='lines+markers',
            line=dict(width=3),
            marker=dict(size=8)
        ))
        
        fig_pareto.update_layout(
            title='口味需求量帕累托分析',
            xaxis_title='口味',
            yaxis=dict(
                title='需求量',
                side='left',
                showgrid=True,
                gridcolor='#e2e8f0'
            ),
            yaxis2=dict(
                title='累计占比 (%)',
                side='right',
                range=[0, 100],
                showgrid=False,
                overlaying='y'
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=400,
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            )
        )
        
        fig_pareto.add_hline(y=80, line_dash="dash", line_color="#ef4444", annotation_text="80% 阈值", annotation_position="right")
        
        st.plotly_chart(fig_pareto, use_container_width=True)
        
        top_20_percent = int(len(pareto_df) * 0.2) if len(pareto_df) > 0 else 0
        if top_20_percent > 0:
            top_contribution = pareto_df.iloc[:top_20_percent]['累计百分比'].iloc[-1]
            st.markdown(f"<div style='margin-top: 16px; padding: 12px; background: #f8fafc; border-radius: 8px;'>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: #374151; font-size: 14px;'>**帕累托法则分析**：前 {top_20_percent} 个口味（约20%）贡献了 **{top_contribution:.1f}%** 的需求量</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    card_container = st.container(border=True)
    with card_container:
        st.markdown("<div class='section-title'>🚨 Top N 问题清单</div>", unsafe_allow_html=True)
        
        gap_df = filtered_df.groupby('营业部').agg({
            '需求量': 'sum',
            '月累排单': 'sum'
        }).reset_index()
        gap_df['差量'] = gap_df['月累排单'] - gap_df['需求量']
        gap_df['差量率'] = round(gap_df['差量'] / gap_df['需求量'] * 100, 1).fillna(0)
        gap_df = gap_df[gap_df['差量'] < 0].sort_values('差量', ascending=True)
        
        total_gap = gap_df['差量'].abs().sum()
        gap_df['累计缺口占比'] = round(gap_df['差量'].abs().cumsum() / total_gap * 100, 1) if total_gap > 0 else 0
        
        top_n_df = gap_df[gap_df['累计缺口占比'] <= 80].head(3)
        
        if len(top_n_df) == 0:
            st.markdown("<div style='padding: 24px; text-align: center; color: #059669; background: #d1fae5; border-radius: 12px;'>🎉 所有营业部均无显著缺量问题！</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="padding: 12px; background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-radius: 8px; border: 1px solid #f59e0b;">
                <p style="color: #92400e; font-size: 14px; margin: 0;"><strong>📊 问题分析</strong>：以下 <span style="color:#dc2626;">{len(top_n_df)} 个营业部</span> 贡献了 <span style="color:#dc2626;">80%以上</span> 的总缺量</p>
            </div>
            """, unsafe_allow_html=True)
            
            cols = st.columns(3)
            for idx, (_, row) in enumerate(top_n_df.iterrows()):
                with cols[idx]:
                    gap_percent = abs(row['差量率'])
                    rank_color = '#dc2626' if idx == 0 else '#f59e0b' if idx == 1 else '#3b82f6'
                    gap_color = '#dc2626' if gap_percent > 50 else '#f59e0b' if gap_percent > 30 else '#3b82f6'
                    
                    if gap_percent > 50:
                        action_text = "🚨 紧急：立即追加排单<br>📞 确认需求准确性"
                    elif gap_percent > 30:
                        action_text = "⚠️ 高优先级：尽快补单<br>🔍 分析缺量原因"
                    else:
                        action_text = "📋 中等优先级：下批次补充"
                    
                    expand_key = f"expand_dept_{row['营业部']}"
                    is_expanded = st.session_state.get(expand_key, False)
                    
                    st.markdown(f"""
                    <div style="border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); overflow: hidden; background: white;">
                        <div style="display: flex; align-items: center; padding: 16px; border-bottom: 1px solid #e5e7eb;">
                            <div style="width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 16px; color: white; background: {rank_color}; margin-right: 12px;">{idx+1}</div>
                            <div style="font-weight: bold; font-size: 17px; color: #1f2937; flex: 1;">{row['营业部']}</div>
                            <div style="font-weight: bold; font-size: 16px; padding: 4px 10px; border-radius: 16px; background: {gap_color}20; color: {gap_color};">{gap_percent}%</div>
                        </div>
                        <div style="padding: 16px;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                                <div style="text-align: center; flex: 1; padding: 8px; background: #f8fafc; border-radius: 8px; margin: 0 3px;">
                                    <div style="font-size: 12px; color: #6b7280; margin-bottom: 2px;">需求量</div>
                                    <div style="font-weight: bold; font-size: 16px; color: #1f2937;">{row['需求量']:.2f}</div>
                                </div>
                                <div style="text-align: center; flex: 1; padding: 8px; background: #f8fafc; border-radius: 8px; margin: 0 3px;">
                                    <div style="font-size: 12px; color: #6b7280; margin-bottom: 2px;">已排单</div>
                                    <div style="font-weight: bold; font-size: 16px; color: #1f2937;">{row['月累排单']:.2f}</div>
                                </div>
                                <div style="text-align: center; flex: 1; padding: 8px; background: #f8fafc; border-radius: 8px; margin: 0 3px;">
                                    <div style="font-size: 12px; color: #6b7280; margin-bottom: 2px;">差量</div>
                                    <div style="font-weight: bold; font-size: 16px; color: {gap_color};">{row['差量']:.2f}</div>
                                </div>
                            </div>
                            <div style="background: #fffbeb; border-radius: 8px; padding: 12px;">
                                <div style="color: #9a3412; font-size: 14px; line-height: 1.8;">{action_text}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    def toggle_expand(dept):
                        st.session_state[f"expand_dept_{dept}"] = not st.session_state.get(f"expand_dept_{dept}", False)
                    
                    st.button(f"查看详情 {'▼' if is_expanded else '▲'}", key=f"btn_click_{row['营业部'].replace(' ', '_')}", on_click=toggle_expand, args=(row['营业部'],), use_container_width=True)
                    
                    if st.session_state.get(expand_key, False):
                        dept_detail = filtered_df[filtered_df['营业部'] == row['营业部']].copy()
                        dept_detail['差量'] = dept_detail['月累排单'] - dept_detail['需求量']
                        dept_detail['差量率'] = round(dept_detail['差量'] / dept_detail['需求量'] * 100, 1).fillna(0)
                        dept_detail = dept_detail[dept_detail['差量'] < 0].sort_values('差量', ascending=True).head(10)
                        
                        if len(dept_detail) > 0:
                            table_rows = ""
                            for _, detail_row in dept_detail.iterrows():
                                gap_rate_color = '#dc2626' if detail_row['差量率'] < -20 else '#3b82f6'
                                taste = str(detail_row['口味'])
                                capacity = str(detail_row['容量'])
                                demand = round(detail_row['需求量'], 2)
                                order = round(detail_row['月累排单'], 2)
                                gap = round(detail_row['差量'], 2)
                                gap_rate = detail_row['差量率']
                                
                                table_rows += f"""<tr style="border-bottom: 1px solid #f1f5f9;"><td style="padding: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{taste}</td><td style="padding: 4px; text-align: right;">{capacity}</td><td style="padding: 4px; text-align: right;">{demand}</td><td style="padding: 4px; text-align: right;">{order}</td><td style="padding: 4px; text-align: right; color: {gap_rate_color};">{gap}</td><td style="padding: 4px; text-align: right; color: {gap_rate_color}; font-weight: 600;">{gap_rate}%</td></tr>"""
                            
                            table_html = f"""<div style="margin-top: 2px; margin-bottom: 12px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.08); overflow: hidden; background: #ffffff; border: 1px solid #e5e7eb;"><div style="padding: 10px; background: #f1f5f9; border-bottom: 1px solid #e2e8f0;"><div style="font-weight: bold; font-size: 13px; color: #334155;">口味容量明细（前10）</div></div><div style="padding: 0; max-height: 220px; overflow-y: auto;"><table style="width: 100%; font-size: 11px; border-collapse: collapse; table-layout: fixed;"><thead style="position: sticky; top: 0; background: #e2e8f0; z-index: 1;"><tr><th style="padding: 5px 4px; text-align: left; font-weight: 600; color: #475569; width: 25%;">口味</th><th style="padding: 5px 4px; text-align: right; font-weight: 600; color: #475569; width: 12%;">容量</th><th style="padding: 5px 4px; text-align: right; font-weight: 600; color: #475569; width: 15%;">需求量</th><th style="padding: 5px 4px; text-align: right; font-weight: 600; color: #475569; width: 15%;">已排单</th><th style="padding: 5px 4px; text-align: right; font-weight: 600; color: #475569; width: 15%;">差量</th><th style="padding: 5px 4px; text-align: right; font-weight: 600; color: #475569; width: 18%;">差量率</th></tr></thead><tbody>{table_rows}</tbody></table></div></div>"""
                            st.markdown(table_html, unsafe_allow_html=True)
                        else:
                            st.markdown("<div style='margin-top: 12px; padding: 12px; background: #d1fae5; border-radius: 8px; text-align: center; color: #059669; font-size: 13px;'>该营业部当前筛选条件下无缺量明细</div>", unsafe_allow_html=True)

    card_container = st.container(border=True)
    with card_container:
        st.markdown("<div class='section-title'>需求与预算对比（口味别）</div>", unsafe_allow_html=True)
        chart_flavor_df = filtered_df.groupby('口味').agg({
            '需求量': 'sum',
            '预算销量': 'sum'
        }).reset_index()
        chart_flavor_df = chart_flavor_df.sort_values('需求量', ascending=False)

        fig_compare = px.bar(chart_flavor_df, y='口味', x=['需求量', '预算销量'],
                             barmode='group', orientation='h', height=600,
                             color_discrete_map={'需求量': '#1e40af', '预算销量': '#60a5fa'})
        fig_compare.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            yaxis=dict(autorange="reversed", showgrid=False),
            xaxis=dict(showgrid=True, gridcolor='#e2e8f0'),
            legend=dict(title=''),
            margin=dict(l=20, r=100, t=20, b=20),
            bargap=0.2,
            bargroupgap=0.3
        )
        fig_compare.update_traces(
            textposition='outside',
            textfont=dict(size=12, weight='bold', color='#1e293b')
        )
        st.plotly_chart(fig_compare, use_container_width=True)

elif st.session_state.current_page == '历史销量':
    SAVE_FILE = 'history_data_cache.pkl'
    from datetime import datetime

    def save_data(df_2026, df_2025, df_budget, material_flavor_map):
        import pickle
        with open(SAVE_FILE, 'wb') as f:
            pickle.dump({
                'df_2026': df_2026,
                'df_2025': df_2025,
                'df_budget': df_budget,
                'material_flavor_map': material_flavor_map
            }, f)

    def load_saved_data():
        import pickle
        import os
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, 'rb') as f:
                    data = pickle.load(f)
                    return data['df_2026'], data['df_2025'], data['df_budget'], data['material_flavor_map']
            except:
                return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {}
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {}

    df_2026_actual, df_2025_actual, df_2026_budget, material_flavor_map = load_saved_data()
    
    if df_2026_actual.empty and df_2025_actual.empty and df_2026_budget.empty:
        import os
        if os.path.exists('2026销量.xlsx'):
            df_2026_actual, df_2025_actual, df_2026_budget, material_flavor_map = cached_load_history_data('2026销量.xlsx')
            save_data(df_2026_actual, df_2025_actual, df_2026_budget, material_flavor_map)
            st.success("已从默认数据文件加载数据！")

    st.markdown("""
        <div class='header-card-history'>
            <div class='header-title'>历史销量分析</div>
            <div class='header-subtitle'>基于2025-2026年实际销量与预算数据</div>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("上传/更新数据", expanded=False):
        uploaded_file = st.file_uploader("选择Excel文件（需包含2026年实际销量、2025年实际销量、2026年预算销量sheet）", 
                                        type=['xlsx'], key=f'history_uploader_new_{st.session_state.get("history_upload_counter", 0)}',
                                        on_change=lambda: st.session_state.update({'history_data_updated': True}))
        if uploaded_file is not None and st.session_state.get('history_data_updated'):
            st.cache_data.clear()
            
            df_2026_actual, df_2025_actual, df_2026_budget, material_flavor_map = cached_load_history_data(uploaded_file)
            save_data(df_2026_actual, df_2025_actual, df_2026_budget, material_flavor_map)
            
            if 'history_upload_counter' not in st.session_state:
                st.session_state.history_upload_counter = 0
            st.session_state.history_upload_counter += 1
            
            st.session_state['history_data_updated'] = False
            st.session_state['history_last_upload_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            st.success(f"数据已刷新并保存！({st.session_state['history_last_upload_time']})")

    material_col = None
    for col in ['物料号', '物料', '物料编号', '产品号', '产品编号', 'ItemCode', 'Item']:
        if col in df_2026_actual.columns:
            material_col = col
            break
    
    if material_col is None and not df_2026_actual.empty:
        print(f"未找到物料号列，可用列: {df_2026_actual.columns.tolist()}")
    
    all_materials_2026 = df_2026_actual[material_col].unique() if not df_2026_actual.empty and material_col else []
    all_materials_2025 = df_2025_actual[material_col].unique() if not df_2025_actual.empty and material_col else []
    all_materials_budget = df_2026_budget[material_col].unique() if not df_2026_budget.empty and material_col else []
    all_materials = set(all_materials_2026) | set(all_materials_2025) | set(all_materials_budget)
    
    available_flavors = []
    available_capacities = []
    available_packages = []
    
    material_to_universal = material_map.get('material_to_universal', {})
    universal_to_attrs = material_map.get('universal_to_attrs', {})
    
    print(f"物料映射状态: material_to_universal大小={len(material_to_universal)}, universal_to_attrs大小={len(universal_to_attrs)}")
    
    if material_map.get('flavors'):
        available_flavors = material_map['flavors']
        print(f"从物料对应关系获取口味: {available_flavors}")
    elif '口味' in df.columns:
        available_flavors = sorted(df['口味'].unique())
        print(f"从主数据获取口味: {available_flavors}")
    
    if material_map.get('capacities'):
        available_capacities = material_map['capacities']
        print(f"从物料对应关系获取容量: {available_capacities}")
    elif '容量' in df.columns:
        available_capacities = sorted(df['容量'].unique())
    
    if material_map.get('packages'):
        available_packages = material_map['packages']
        print(f"从物料对应关系获取内包装: {available_packages}")
    elif '内包装' in df.columns:
        available_packages = sorted(df['内包装'].unique())

    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

    with col1:
        history_region = st.selectbox('行销区域', ['全部'] + list(REGION_DEPT_MAP.keys()), key='history_region')

    with col2:
        if df_2026_actual.empty:
            history_dept_options = ['全部']
        else:
            if history_region == '全部':
                all_depts = []
                for depts in REGION_DEPT_MAP.values():
                    all_depts.extend(depts)
                history_dept_options = ['全部'] + list(set(all_depts) & set(df_2026_actual['营业部'].unique()))
            else:
                history_dept_options = ['全部'] + [d for d in REGION_DEPT_MAP[history_region] if d in df_2026_actual['营业部'].unique()]
        history_dept = st.selectbox('营业部', history_dept_options, key='history_dept')

    with col3:
        history_project = st.selectbox('专案', ['全部'] + list(project_map.keys()), key='history_project')

    with col4:
        history_product30 = st.selectbox('3.0新品', ['全部'] + list(product30_map.keys()), key='history_product30')

    with col5:
        history_product20 = st.selectbox('2.0产品', ['全部'] + list(product20_map.keys()), key='history_product20')

    filtered_flavors = available_flavors.copy()
    if project_map and history_project != '全部':
        filtered_flavors = [f for f in filtered_flavors if f in project_map.get(history_project, [])]
    if product30_map and history_product30 != '全部':
        filtered_flavors = [f for f in filtered_flavors if f in product30_map.get(history_product30, [])]
    if product20_map and history_product20 != '全部':
        filtered_flavors = [f for f in filtered_flavors if f in product20_map.get(history_product20, [])]

    with col6:
        history_flavor = st.selectbox('口味', ['全部'] + filtered_flavors, key='history_flavor_new')

    dynamic_capacities = available_capacities
    active_flavors = []
    if history_flavor != '全部':
        active_flavors = [history_flavor]
    elif filtered_flavors:
        active_flavors = filtered_flavors
    
    if active_flavors and material_map.get('material_to_universal') and material_map.get('universal_to_attrs'):
        capacity_set = set()
        for universal, attrs in material_map['universal_to_attrs'].items():
            flavors = attrs.get('flavors', [])
            if any(f in active_flavors for f in flavors):
                capacities = attrs.get('capacities', [])
                capacity_set.update(capacities)
        dynamic_capacities = sorted([c for c in capacity_set if c])

    with col7:
        history_capacity = st.selectbox('容量', ['全部'] + dynamic_capacities, key='history_capacity_new')

    dynamic_packages = available_packages
    if active_flavors and material_map.get('material_to_universal') and material_map.get('universal_to_attrs'):
        package_set = set()
        for universal, attrs in material_map['universal_to_attrs'].items():
            flavors = attrs.get('flavors', [])
            if any(f in active_flavors for f in flavors):
                packages = attrs.get('packages', [])
                package_set.update(packages)
        dynamic_packages = sorted([p for p in package_set if p])

    with col8:
        history_package = st.selectbox('内包装', ['全部'] + dynamic_packages, key='history_package_new')
    
    all_months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
    
    available_months_set = set()
    if '月份' in df_2026_actual.columns:
        available_months_set.update(df_2026_actual['月份'].astype(str).unique())
    if '月份' in df_2025_actual.columns:
        available_months_set.update(df_2025_actual['月份'].astype(str).unique())
    if '月份' in df_2026_budget.columns:
        available_months_set.update(df_2026_budget['月份'].astype(str).unique())
    
    available_months = [m for m in all_months if m in available_months_set]
    
    # 强制重置月份选择状态，清除之前的缓存
    # 取消下面一行的注释来重置状态
    # st.session_state.pop('history_month_multi', None)
    
    # 确保状态初始化为空列表
    if 'history_month_multi' not in st.session_state or st.session_state.history_month_multi is None:
        st.session_state.history_month_multi = []
    

    

    
    # 使用Streamlit原生按钮和columns，配合简单的CSS
    import time
    ts = int(time.time())
    
    st.markdown("""
        <style>
        .month-label-""" + str(ts) + """ {
            background: linear-gradient(135deg, #4285f4 0%, #1a73e8 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 500;
            font-size: 14px;
            cursor: default;
            text-align: center;
            min-width: 60px;
            box-sizing: border-box;
            display: inline-block;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # 创建columns来横向排列
    num_cols = 3 + len(available_months)
    cols = st.columns(num_cols, gap="small")
    
    # 月份标签
    with cols[0]:
        st.markdown(f'<div class="month-label-{ts}">月份</div>', unsafe_allow_html=True)
    
    # 全选按钮
    with cols[1]:
        if st.button('全选', key='month_select_all'):
            st.session_state.history_month_multi = available_months[:]
            st.rerun()
    
    # 清空按钮
    with cols[2]:
        if st.button('清空', key='month_clear_all'):
            st.session_state.history_month_multi = []
            st.rerun()
    
    # 月份选择按钮
    for i, month in enumerate(available_months):
        with cols[3 + i]:
            is_selected = month in st.session_state.history_month_multi
            if st.button(month, key=f'month_{month}', type='primary' if is_selected else 'secondary'):
                if month in st.session_state.history_month_multi:
                    st.session_state.history_month_multi.remove(month)
                else:
                    st.session_state.history_month_multi.append(month)
                st.rerun()
    
    selected_months = st.session_state.history_month_multi

    flavor_to_materials = precompute_flavor_materials(material_map)
    capacity_to_materials = precompute_capacity_materials(material_map)
    package_to_materials = precompute_package_materials(material_map)

    material_to_universal = material_map.get('material_to_universal', {})
    universal_to_attrs = material_map.get('universal_to_attrs', {})

    def add_attrs_from_material(df, material_col, material_to_universal, universal_to_attrs):
        if df.empty or material_col is None or material_col not in df.columns:
            return df
        
        df_copy = df.copy()
        
        material_str_series = df_copy[material_col].astype(str).str.strip()
        
        attr_cache = {}
        for material_str in material_str_series.unique():
            if pd.isna(material_str) or material_str == 'nan':
                attr_cache[material_str] = {'flavors': None, 'capacities': None, 'packages': None}
                continue
            
            result = {'flavors': None, 'capacities': None, 'packages': None}
            
            if material_str in material_to_universal:
                universal = material_to_universal[material_str]
                if universal in universal_to_attrs:
                    attrs = universal_to_attrs[universal]
                    for attr_name in ['flavors', 'capacities', 'packages']:
                        attr_list = attrs.get(attr_name, [])
                        if attr_list:
                            result[attr_name] = attr_list[0]
            else:
                for key in material_to_universal:
                    if key in material_str or material_str in key:
                        universal = material_to_universal[key]
                        if universal in universal_to_attrs:
                            attrs = universal_to_attrs[universal]
                            for attr_name in ['flavors', 'capacities', 'packages']:
                                attr_list = attrs.get(attr_name, [])
                                if attr_list:
                                    result[attr_name] = attr_list[0]
                            break
            
            attr_cache[material_str] = result
        
        df_copy['口味'] = material_str_series.map(lambda x: attr_cache.get(x, {}).get('flavors'))
        df_copy['容量'] = material_str_series.map(lambda x: attr_cache.get(x, {}).get('capacities'))
        df_copy['内包装'] = material_str_series.map(lambda x: attr_cache.get(x, {}).get('packages'))
        
        return df_copy

    df_2026_actual_with_attrs = add_attrs_from_material(df_2026_actual, material_col, material_to_universal, universal_to_attrs)
    df_2025_actual_with_attrs = add_attrs_from_material(df_2025_actual, material_col, material_to_universal, universal_to_attrs)
    df_2026_budget_with_attrs = add_attrs_from_material(df_2026_budget, material_col, material_to_universal, universal_to_attrs)

    filtered_2026 = filter_data(df_2026_actual_with_attrs, history_region, history_dept, selected_months, history_flavor, history_capacity, history_package, history_project, history_product30, history_product20, REGION_DEPT_MAP, flavor_to_materials, capacity_to_materials, package_to_materials, project_map, product30_map, product20_map, material_col)
    filtered_2025 = filter_data(df_2025_actual_with_attrs, history_region, history_dept, selected_months, history_flavor, history_capacity, history_package, history_project, history_product30, history_product20, REGION_DEPT_MAP, flavor_to_materials, capacity_to_materials, package_to_materials, project_map, product30_map, product20_map, material_col)
    filtered_budget = filter_data(df_2026_budget_with_attrs, history_region, history_dept, selected_months, history_flavor, history_capacity, history_package, history_project, history_product30, history_product20, REGION_DEPT_MAP, flavor_to_materials, capacity_to_materials, package_to_materials, project_map, product30_map, product20_map, material_col)

    if 'selected_capacity' not in st.session_state:
        st.session_state.selected_capacity = None
    if 'clear_selection_triggered' not in st.session_state:
        st.session_state.clear_selection_triggered = False

    filtered_2026_for_source_chart = filtered_2026.copy()
    filtered_2025_for_source_chart = filtered_2025.copy()

    if st.session_state.selected_capacity:
        selected_capacity_str = str(st.session_state.selected_capacity)
        if '容量' in filtered_2026.columns:
            filtered_2026 = filtered_2026[filtered_2026['容量'].astype(str) == selected_capacity_str]
        if '容量' in filtered_2025.columns:
            filtered_2025 = filtered_2025[filtered_2025['容量'].astype(str) == selected_capacity_str]
        if '容量' in filtered_budget.columns:
            filtered_budget = filtered_budget[filtered_budget['容量'].astype(str) == selected_capacity_str]

    with st.expander("筛选结果调试", expanded=False):
        st.write(f"筛选条件 - 口味: {history_flavor}, 容量: {history_capacity}, 内包装: {history_package}")
        st.write(f"原始2026数据行数: {len(df_2026_actual)}, 筛选后: {len(filtered_2026)}")
        st.write(f"原始2025数据行数: {len(df_2025_actual)}, 筛选后: {len(filtered_2025)}")
        st.write(f"原始预算数据行数: {len(df_2026_budget)}, 筛选后: {len(filtered_budget)}")
        
        if history_flavor != '全部':
            st.write(f"口味 '{history_flavor}' 筛选结果检查:")
            if len(filtered_2026) == 0:
                st.warning("筛选后2026数据为空！")
            else:
                st.success("筛选后2026数据不为空")
        
        if '物料号' in df_2026_actual.columns:
            original_materials = set(df_2026_actual['物料号'].astype(str).str.strip())
            filtered_materials = set(filtered_2026['物料号'].astype(str).str.strip()) if not filtered_2026.empty else set()
            st.write(f"物料号数量变化: {len(original_materials)} -> {len(filtered_materials)}")

    sales_col = None
    if not df_2026_actual.empty:
        for col in df_2026_actual.columns:
            col_str = str(col)
            if '销量' in col_str or 'Qty' in col_str or 'amount' in col_str.lower() or 'sales' in col_str.lower():
                sales_col = col
                break
        if sales_col is None:
            numeric_cols = df_2026_actual.select_dtypes(include=[int, float]).columns
            if len(numeric_cols) > 0:
                sales_col = numeric_cols[0]
            elif len(df_2026_actual.columns) > 3:
                sales_col = df_2026_actual.columns[3]
            else:
                sales_col = df_2026_actual.columns[-1] if len(df_2026_actual.columns) > 0 else None
    
    budget_col = None
    if not df_2026_budget.empty:
        for col in df_2026_budget.columns:
            col_str = str(col)
            if '预算' in col_str or 'budget' in col_str.lower():
                budget_col = col
                break
        if budget_col is None:
            numeric_cols = df_2026_budget.select_dtypes(include=[int, float]).columns
            budget_col = numeric_cols[0] if len(numeric_cols) > 0 else (df_2026_budget.columns[-1] if len(df_2026_budget.columns) > 0 else '预算销量')
    else:
        budget_col = '预算销量'
    
    def calculate_total(df, sales_col):
        if df.empty:
            return 0
        if sales_col in df.columns:
            return pd.to_numeric(df[sales_col], errors='coerce').sum()
        else:
            numeric_cols = df.select_dtypes(include=[int, float]).columns
            if len(numeric_cols) > 0:
                return df[numeric_cols].sum().sum()
            elif len(df.columns) > 3:
                return df.iloc[:, 3:].sum().sum()
            return 0
    
    total_2026 = calculate_total(filtered_2026, sales_col)
    total_2025 = calculate_total(filtered_2025, sales_col)
    total_budget = calculate_total(filtered_budget, budget_col)
    growth_rate = ((total_2026 - total_2025) / total_2025 * 100) if total_2025 > 0 else 0
    budget_achievement = (total_2026 / total_budget * 100) if total_budget > 0 else 0
    
    months_order = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
    mom_growth_rate = None
    
    selected_months_list = st.session_state.history_month_multi if 'history_month_multi' in st.session_state else []
    
    if len(selected_months_list) == 1 and sales_col in df_2026_actual.columns:
        selected_month = selected_months_list[0]
        if selected_month in months_order:
            month_idx = months_order.index(selected_month)
            current_month_sales = df_2026_actual[df_2026_actual['月份'] == selected_month][sales_col].sum()
            
            if month_idx == 0:
                prev_month = '12月'
                prev_month_sales = df_2025_actual[df_2025_actual['月份'] == prev_month][sales_col].sum()
            else:
                prev_month = months_order[month_idx - 1]
                prev_month_sales = df_2026_actual[df_2026_actual['月份'] == prev_month][sales_col].sum()
            
            if prev_month_sales > 0:
                mom_growth_rate = ((current_month_sales - prev_month_sales) / prev_month_sales * 100)

    growth_card_class = 'metric-card-red' if growth_rate < 0 else 'metric-card-green'
    growth_value_class = 'metric-value-red' if growth_rate < 0 else 'metric-value-green'
    growth_trend_icon = '↓' if growth_rate < 0 else '↑'
    growth_trend_color = '#dc2626' if growth_rate < 0 else '#059669'
    
    if mom_growth_rate is not None:
        mom_card_class = 'metric-card-red' if mom_growth_rate < 0 else 'metric-card-blue'
        mom_value_class = 'metric-value-red' if mom_growth_rate < 0 else 'metric-value-blue'
        mom_trend_icon = '↓' if mom_growth_rate < 0 else '↑'
        mom_trend_color = '#dc2626' if mom_growth_rate < 0 else '#1e40af'
        mom_display_value = f"{mom_growth_rate:.2f}%"
        mom_trend_text = f"{mom_trend_icon} {'环比下降' if mom_growth_rate < 0 else '环比增长'}"
    else:
        mom_card_class = 'metric-card-gray'
        mom_value_class = 'metric-value-gray'
        mom_display_value = '-'
        mom_trend_text = ''
        mom_trend_color = '#9ca3af'

    st.markdown(f"""
        <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 20px; margin-bottom: 24px;'>
            <div class='metric-card-purple'>
                <div class='metric-value-purple'>{total_2026:.2f}</div>
                <div class='metric-label'>2026年实际销量</div>
            </div>
            <div class='metric-card-purple'>
                <div class='metric-value-purple'>{total_2025:.2f}</div>
                <div class='metric-label'>2025年实际销量</div>
            </div>
            <div class='metric-card-purple'>
                <div class='metric-value-purple'>{total_budget:.2f}</div>
                <div class='metric-label'>2026年预算销量</div>
            </div>
            <div class='{growth_card_class}'>
                <div class='{growth_value_class}'>{growth_rate:.2f}%</div>
                <div class='metric-label'>同比增长率</div>
                <div class='metric-trend' style='color: {growth_trend_color};'>
                    <span style='margin-right: 4px;'>{growth_trend_icon}</span>
                    {growth_trend_color == '#dc2626' and '同比下降' or '同比增长'}
                </div>
            </div>
            <div class='{mom_card_class}'>
                <div class='{mom_value_class}'>{mom_display_value}</div>
                <div class='metric-label'>环比增长率</div>
                <div class='metric-trend' style='color: {mom_trend_color};'>{mom_trend_text}</div>
            </div>
            <div class='metric-card-orange'>
                <div class='metric-value-orange'>{budget_achievement:.2f}%</div>
                <div class='metric-label'>预算达成率</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    filtered_2026_with_attrs = filtered_2026_for_source_chart
    filtered_2025_with_attrs = filtered_2025_for_source_chart
    filtered_budget_with_attrs = filtered_budget

    def clear_selection():
        st.session_state.selected_capacity = None
        st.session_state.clear_selection_triggered = True
        if 'capacity_growth_chart' in st.session_state:
            del st.session_state['capacity_growth_chart']
    
    col_reset = st.columns([1, 10])
    with col_reset[0]:
        if st.session_state.selected_capacity:
            st.button('清除筛选', on_click=clear_selection, use_container_width=True)
    
    st.session_state.clear_selection_triggered = False
    
    if st.session_state.selected_capacity:
        st.markdown(f"<div style='padding: 8px 16px; background-color: #FEF3C7; border-radius: 8px; color: #D97706; font-weight: bold; margin-bottom: 16px;'>当前筛选: 容量 = {st.session_state.selected_capacity}</div>", unsafe_allow_html=True)

    col_new1, col_new2, col_new3 = st.columns(3, gap='medium')

    with col_new1:
        st.markdown("<div class='section-title-purple'>较同期成长（容量别）</div>", unsafe_allow_html=True)
        st.markdown("<div class='chart-scroll-container'>", unsafe_allow_html=True)
        
        has_capacity_2026 = '容量' in filtered_2026_with_attrs.columns and filtered_2026_with_attrs['容量'].notna().any()
        has_capacity_2025 = '容量' in filtered_2025_with_attrs.columns and filtered_2025_with_attrs['容量'].notna().any()
        
        if has_capacity_2026 and has_capacity_2025 and sales_col and sales_col in filtered_2026_with_attrs.columns and sales_col in filtered_2025_with_attrs.columns:
            capacity_growth_df = pd.DataFrame()
            capacity_2026 = filtered_2026_with_attrs[filtered_2026_with_attrs['容量'].notna()].groupby('容量')[sales_col].sum().reset_index()
            capacity_2025 = filtered_2025_with_attrs[filtered_2025_with_attrs['容量'].notna()].groupby('容量')[sales_col].sum().reset_index()
            
            capacity_growth_df = pd.merge(capacity_2026, capacity_2025, on='容量', suffixes=('_2026', '_2025'))
            capacity_growth_df = capacity_growth_df[capacity_growth_df['容量'].notna() & (capacity_growth_df['容量'] != '')]
            capacity_growth_df['成长率'] = ((capacity_growth_df[f'{sales_col}_2026'] - capacity_growth_df[f'{sales_col}_2025']) / capacity_growth_df[f'{sales_col}_2025'] * 100).fillna(0)
            capacity_growth_df = capacity_growth_df[~capacity_growth_df['成长率'].isin([float('inf'), float('-inf')])]
            capacity_growth_df = capacity_growth_df.sort_values('成长率', ascending=False)
            
            fig_capacity_growth = go.Figure()
            
            colors = ['#059669' if x >= 0 else '#dc2626' for x in capacity_growth_df['成长率']]
            
            fig_capacity_growth.add_trace(go.Bar(
                y=capacity_growth_df['容量'],
                x=capacity_growth_df['成长率'],
                orientation='h',
                marker_color=colors,
                marker_cornerradius=4,
                text=capacity_growth_df['成长率'].apply(lambda x: f'+{x:.2f}%' if x >= 0 else f'{x:.2f}%'),
                textposition='inside',
                insidetextanchor='middle',
                textfont=dict(size=11, weight='bold', color='#ffffff'),
                hovertemplate='销量: %{customdata:.2f}<extra></extra>',
                customdata=capacity_growth_df[f'{sales_col}_2026'],
                hoverlabel=dict(font=dict(size=14, weight='bold'))
            ))
            
            max_abs_value = abs(capacity_growth_df['成长率']).max() if len(capacity_growth_df) > 0 else 10
            x_range = min(max_abs_value * 1.3, 100)
            
            fig_capacity_growth.update_layout(
                plot_bgcolor='rgba(248,250,252,1)',
                paper_bgcolor='rgba(255,255,255,0)',
                yaxis=dict(
                    type='category',
                    showgrid=False,
                    tickfont=dict(size=12, color='#374151'),
                    categoryorder='array',
                    categoryarray=capacity_growth_df['容量'].astype(str).tolist()[::-1]
                ),
                xaxis=dict(
                    title=dict(text='成长率 (%)', font=dict(size=11, color='#6B7280')),
                    showgrid=True,
                    gridcolor='#E5E7EB',
                    gridwidth=1,
                    showline=False,
                    zeroline=True,
                    zerolinecolor='#DC2626',
                    zerolinewidth=2,
                    showticklabels=True,
                    tickfont=dict(size=11, color='#6B7280'),
                    range=[-x_range, x_range]
                ),
                margin=dict(l=60, r=60, t=20, b=20),
                height=300,
                showlegend=False,
                dragmode='zoom'
            )
            
            capacity_event = st.plotly_chart(fig_capacity_growth, use_container_width=True, key='capacity_growth_chart', on_select="rerun", config={'scrollZoom': True})
            
            if capacity_event and hasattr(capacity_event, 'selection') and capacity_event.selection.points:
                selected_y = capacity_event.selection.points[0].get('y')
                if selected_y:
                    st.session_state.selected_capacity = selected_y
            elif not st.session_state.get('clear_selection_triggered'):
                selected_points = st.session_state.get('capacity_growth_chart', {}).get('selection', {}).get('points', [])
                if selected_points:
                    st.session_state.selected_capacity = selected_points[0].get('y')
            
            if st.session_state.selected_capacity:
                st.markdown(f"<div style='font-size: 12px; color: #6B7280; text-align: center;'>已选择容量: {st.session_state.selected_capacity}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='text-align: center; color: #9ca3af; padding-top: 60px;'>无法获取容量信息</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

    with col_new2:
        st.markdown("<div class='section-title-purple'>预算达成（容量别）</div>", unsafe_allow_html=True)
        st.markdown("<div class='chart-scroll-container'>", unsafe_allow_html=True)
        
        has_capacity_actual = '容量' in filtered_2026_with_attrs.columns and filtered_2026_with_attrs['容量'].notna().any()
        has_capacity_budget = '容量' in filtered_budget_with_attrs.columns and filtered_budget_with_attrs['容量'].notna().any()
        
        if has_capacity_actual and has_capacity_budget and sales_col and budget_col and sales_col in filtered_2026_with_attrs.columns and budget_col in filtered_budget_with_attrs.columns:
            capacity_budget_df = pd.DataFrame()
            
            actual_data = filtered_2026_with_attrs[filtered_2026_with_attrs['容量'].notna()]
            budget_data = filtered_budget_with_attrs[filtered_budget_with_attrs['容量'].notna()]
            
            capacity_actual = actual_data.groupby('容量')[sales_col].sum().reset_index()
            capacity_budget = budget_data.groupby('容量')[budget_col].sum().reset_index()
            
            capacity_budget_df = pd.merge(capacity_actual, capacity_budget, on='容量', suffixes=('_actual', '_budget'))
            capacity_budget_df = capacity_budget_df[capacity_budget_df['容量'].notna() & (capacity_budget_df['容量'] != '')]
            
            actual_col = f'{sales_col}_actual' if f'{sales_col}_actual' in capacity_budget_df.columns else sales_col
            budget_col_merged = f'{budget_col}_budget' if f'{budget_col}_budget' in capacity_budget_df.columns else budget_col
            
            capacity_budget_df['达成率'] = (capacity_budget_df[actual_col] / capacity_budget_df[budget_col_merged] * 100).fillna(0)
            capacity_budget_df = capacity_budget_df[~capacity_budget_df['达成率'].isin([float('inf'), float('-inf')])]
            capacity_budget_df = capacity_budget_df.sort_values('达成率', ascending=False)
            
            fig_capacity_budget = go.Figure()
            
            colors = ['#059669' if x >= 100 else '#3B82F6' if x >= 80 else '#dc2626' for x in capacity_budget_df['达成率']]
            
            fig_capacity_budget.add_trace(go.Bar(
                y=capacity_budget_df['容量'],
                x=capacity_budget_df['达成率'],
                orientation='h',
                marker_color=colors,
                marker_cornerradius=4,
                text=capacity_budget_df['达成率'].apply(lambda x: f'{x:.1f}%'),
                textposition='outside',
                insidetextanchor='middle',
                textfont=dict(size=12, weight='bold', color='#334155'),
                hovertemplate='达成率: %{x:.1f}%<br>实际销量: %{customdata:.2f}<br>预算销量: %{customdata2:.2f}<extra></extra>',
                customdata=capacity_budget_df[[actual_col, budget_col_merged]].values.tolist(),
                hoverlabel=dict(font=dict(size=14, weight='bold'))
            ))
            
            max_value = capacity_budget_df['达成率'].max() if len(capacity_budget_df) > 0 else 100
            x_range = max(max_value * 1.2, 100)
            
            fig_capacity_budget.update_layout(
                plot_bgcolor='rgba(248,250,252,1)',
                paper_bgcolor='rgba(255,255,255,0)',
                yaxis=dict(
                    type='category',
                    showgrid=False,
                    tickfont=dict(size=12, color='#374151'),
                    categoryorder='array',
                    categoryarray=capacity_budget_df['容量'].astype(str).tolist()[::-1]
                ),
                xaxis=dict(
                    title=dict(text='预算达成率 (%)', font=dict(size=11, color='#6B7280')),
                    showgrid=True,
                    gridcolor='#E5E7EB',
                    gridwidth=1,
                    showline=False,
                    zeroline=False,
                    showticklabels=True,
                    tickfont=dict(size=11, color='#6B7280'),
                    range=[0, x_range]
                ),
                margin=dict(l=60, r=60, t=20, b=20),
                height=300,
                showlegend=False,
                dragmode='zoom'
            )
        
            st.plotly_chart(fig_capacity_budget, use_container_width=True, config={'scrollZoom': True})
        else:
            st.markdown("<div style='text-align: center; color: #9ca3af; padding-top: 60px;'>无法获取容量或预算信息</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    with col_new3:
        card_container = st.container(border=True)
        with card_container:
            st.markdown("<div class='section-title-purple'>26年实际销量（月分别）</div>", unsafe_allow_html=True)
            
            if '月份' in filtered_2026.columns and sales_col and sales_col in filtered_2026.columns:
                monthly_data = filtered_2026.copy()
                
                monthly_sales_2026 = monthly_data.groupby('月份')[sales_col].sum().reindex(months_order, fill_value=0).reset_index()
                
                fig_monthly_2026 = go.Figure()
                fig_monthly_2026.add_trace(go.Bar(
                    x=monthly_sales_2026['月份'],
                    y=monthly_sales_2026[sales_col],
                    marker_color='#3B82F6',
                    marker_line_width=0,
                    marker_cornerradius=6,
                    text=monthly_sales_2026[sales_col].apply(lambda x: f'{x:.0f}' if x > 0 else ''),
                    textposition='outside',
                    textfont=dict(size=11, weight='bold', color='#1D4ED8')
                ))
                fig_monthly_2026.update_layout(
                    plot_bgcolor='rgba(248,250,252,1)',
                    paper_bgcolor='rgba(255,255,255,0)',
                    yaxis=dict(
                        title=dict(text='销量', font=dict(size=11, color='#6B7280')),
                        showgrid=True,
                        gridcolor='#E5E7EB',
                        gridwidth=1,
                        showline=False,
                        zeroline=True,
                        zerolinecolor='#9CA3AF',
                        zerolinewidth=1,
                        tickfont=dict(size=11, color='#6B7280')
                    ),
                    xaxis=dict(
                        showgrid=False,
                        showline=False,
                        showticklabels=True,
                        tickfont=dict(size=11, color='#374151')
                    ),
                    margin=dict(l=50, r=50, t=20, b=50),
                    height=300,
                    showlegend=False
                )
                st.plotly_chart(fig_monthly_2026, use_container_width=True)
            else:
                st.markdown("<div style='text-align: center; color: #9ca3af; padding-top: 60px;'>数据中不含月份列或销量列</div>", unsafe_allow_html=True)

    def convert_month(month_val):
        try:
            if isinstance(month_val, pd.Timestamp) or ('/' in str(month_val) or '-' in str(month_val)):
                return f"{pd.to_datetime(month_val).month}月"
            return str(month_val)
        except:
            return str(month_val)

    if '月份' in filtered_2026.columns:
        filtered_2026['月份'] = filtered_2026['月份'].apply(convert_month)
    if '月份' in filtered_2025.columns:
        filtered_2025['月份'] = filtered_2025['月份'].apply(convert_month)
    if '月份' in filtered_budget.columns:
        filtered_budget['月份'] = filtered_budget['月份'].apply(convert_month)

    if sales_col and sales_col in filtered_2026.columns:
        filtered_2026[sales_col] = pd.to_numeric(filtered_2026[sales_col], errors='coerce').fillna(0)
    if sales_col and sales_col in filtered_2025.columns:
        filtered_2025[sales_col] = pd.to_numeric(filtered_2025[sales_col], errors='coerce').fillna(0)
    if budget_col and budget_col in filtered_budget.columns:
        filtered_budget[budget_col] = pd.to_numeric(filtered_budget[budget_col], errors='coerce').fillna(0)
    
    filtered_2026_for_compare = filtered_2026.copy()
    filtered_2025_for_compare = filtered_2025.copy()
    filtered_budget_for_compare = filtered_budget.copy()
    
    if '月份' in filtered_2026_for_compare.columns and sales_col:
        monthly_2026 = filtered_2026_for_compare.groupby('月份')[sales_col].sum().reindex(months_order, fill_value=0).reset_index()
    else:
        monthly_2026 = pd.DataFrame({'月份': months_order, '销量': [0]*12})
        if sales_col:
            monthly_2026 = monthly_2026.rename(columns={'销量': sales_col})
    
    if '月份' in filtered_2025_for_compare.columns and sales_col:
        monthly_2025 = filtered_2025_for_compare.groupby('月份')[sales_col].sum().reindex(months_order, fill_value=0).reset_index()
    else:
        monthly_2025 = pd.DataFrame({'月份': months_order, '销量': [0]*12})
        if sales_col:
            monthly_2025 = monthly_2025.rename(columns={'销量': sales_col})
    
    if '月份' in filtered_budget_for_compare.columns:
        monthly_budget = filtered_budget_for_compare.groupby('月份')[budget_col].sum().reindex(months_order, fill_value=0).reset_index()
    else:
        monthly_budget = pd.DataFrame({'月份': months_order, budget_col: [0]*12})

    monthly_compare = pd.merge(monthly_2026, monthly_2025, on='月份', suffixes=('_2026', '_2025'))
    monthly_compare = pd.merge(monthly_compare, monthly_budget, on='月份')
    
    monthly_compare['增长率'] = monthly_compare.apply(
        lambda row: ((row[f'{sales_col}_2026'] - row[f'{sales_col}_2025']) / row[f'{sales_col}_2025'] * 100)
        if row[f'{sales_col}_2025'] > 0 else None,
        axis=1
    )
    
    monthly_compare['预算达成'] = monthly_compare.apply(
        lambda row: (row[f'{sales_col}_2026'] / row[budget_col] * 100)
        if row[budget_col] > 0 else None,
        axis=1
    )

    def create_trend_chart(monthly_compare, sales_col):
        
        fig_trend = go.Figure()
        
        max_val = max(monthly_compare[f'{sales_col}_2026'].max(), monthly_compare[f'{sales_col}_2025'].max()) if len(monthly_compare) > 0 else 1
        max_range = max_val * 1.3
        
        for i, row in monthly_compare.iterrows():
            x_val = i
            
            fig_trend.add_trace(go.Bar(
                x=[x_val, x_val],
                y=[0, max_range],
                marker_color='#F3F4F6',
                marker_line_width=0,
                showlegend=False,
                hoverinfo='none',
                opacity=0.5,
                width=0.6
            ))
            
            fig_trend.add_trace(go.Bar(
                x=[x_val, x_val],
                y=[0, row[f'{sales_col}_2025']],
                marker_color='#93C5FD',
                marker_line_width=0,
                showlegend=False if i > 0 else True,
                name='25年销量',
                hovertemplate=f'25年销量: {row[f"{sales_col}_2025"]:.0f}<extra></extra>',
                width=0.45
            ))
            
            fig_trend.add_trace(go.Bar(
                x=[x_val, x_val],
                y=[0, row[f'{sales_col}_2026']],
                marker_color='#3B82F6',
                marker_line_width=0,
                showlegend=False if i > 0 else True,
                name='26年销量',
                hovertemplate=f'26年销量: {row[f"{sales_col}_2026"]:.0f}<extra></extra>',
                width=0.3
            ))
            
            if pd.notna(row['增长率']) and abs(row['增长率']) != float('inf'):
                arrow = '↑' if row['增长率'] >= 0 else '↓'
                arrow_color = '#166534' if row['增长率'] >= 0 else '#dc2626'
                text = f"{arrow}{abs(row['增长率']):.1f}%"
                
                fig_trend.add_annotation(
                    x=x_val,
                    y=max(row[f'{sales_col}_2026'], row[f'{sales_col}_2025']) + max_range * 0.08,
                    text=text,
                    showarrow=False,
                    font=dict(color=arrow_color, size=11, weight='bold'),
                    xanchor='center',
                    yanchor='bottom'
                )
        
        fig_trend.update_layout(
            plot_bgcolor='rgba(248,250,252,1)',
            paper_bgcolor='rgba(255,255,255,0)',
            xaxis=dict(
                title='',
                showgrid=False,
                showline=False,
                tickfont=dict(size=12, color='#374151'),
                tickvals=list(range(len(monthly_compare))),
                ticktext=monthly_compare['月份'].tolist()
            ),
            yaxis=dict(
                title=dict(text='销量', font=dict(size=12, color='#6B7280')),
                showgrid=True,
                gridcolor='#E5E7EB',
                gridwidth=1,
                showline=False,
                zeroline=True,
                zerolinecolor='#9CA3AF',
                zerolinewidth=1,
                tickfont=dict(size=11, color='#6B7280'),
                range=[0, max_range]
            ),
            legend=dict(title='', orientation='h', y=-0.15, x=0.5, xanchor='center', font=dict(size=12)),
            margin=dict(l=60, r=40, t=60, b=70),
            height=360,
            showlegend=True,
            barmode='overlay'
        )
        
        return fig_trend

    col1, col2 = st.columns(2, gap='medium')

    with col1:
        card_container = st.container(border=True)
        with card_container:
            st.markdown("<div class='section-title-purple'>25-26年销量对比（含成长率）</div>", unsafe_allow_html=True)
            fig_trend = create_trend_chart(monthly_compare, sales_col)
            st.plotly_chart(fig_trend, use_container_width=True)

    with col2:
        card_container = st.container(border=True)
        with card_container:
            st.markdown("<div class='section-title-purple'>26年预算达成分析</div>", unsafe_allow_html=True)

            
            fig_budget = go.Figure()
            
            max_val = max(monthly_compare[f'{sales_col}_2026'].max(), monthly_compare[budget_col].max()) if len(monthly_compare) > 0 else 1
            max_range = max_val * 1.3
            
            for i, row in monthly_compare.iterrows():
                x_val = i
                
                fig_budget.add_trace(go.Bar(
                    x=[x_val, x_val],
                    y=[0, max_range],
                    marker_color='#F3F4F6',
                    marker_line_width=0,
                    showlegend=False,
                    hoverinfo='none',
                    opacity=0.5,
                    width=0.6
                ))
                
                fig_budget.add_trace(go.Bar(
                    x=[x_val, x_val],
                    y=[0, row[budget_col]],
                    marker_color='#FCD34D',
                    marker_line_width=0,
                    showlegend=False if i > 0 else True,
                    name='预算',
                    hovertemplate=f'预算: {row[budget_col]:.0f}<extra></extra>',
                    width=0.45
                ))
                
                fig_budget.add_trace(go.Bar(
                    x=[x_val, x_val],
                    y=[0, row[f'{sales_col}_2026']],
                    marker_color='#3B82F6',
                    marker_line_width=0,
                    showlegend=False if i > 0 else True,
                    name='销量',
                    hovertemplate=f'销量: {row[f"{sales_col}_2026"]:.0f}<extra></extra>',
                    width=0.3
                ))
                
                if row[f'{sales_col}_2026'] > 0:
                    arrow_color = '#166534' if row['预算达成'] >= 100 else '#dc2626'
                    arrow = '↑' if row['预算达成'] >= 100 else '↓'
                    text = f"{arrow}{row['预算达成']:.1f}%"
                    
                    fig_budget.add_annotation(
                        x=x_val,
                        y=max(row[f'{sales_col}_2026'], row[budget_col]) + max_range * 0.08,
                        text=text,
                        showarrow=False,
                        font=dict(color=arrow_color, size=11, weight='bold'),
                        xanchor='center',
                        yanchor='bottom'
                    )
            
            fig_budget.update_layout(
                plot_bgcolor='rgba(248,250,252,1)',
                paper_bgcolor='rgba(255,255,255,0)',
                xaxis=dict(
                    title='',
                    showgrid=False,
                    showline=False,
                    tickfont=dict(size=12, color='#374151'),
                    tickvals=list(range(len(monthly_compare))),
                    ticktext=monthly_compare['月份'].tolist()
                ),
                yaxis=dict(
                    title=dict(text='销量', font=dict(size=12, color='#6B7280')),
                    showgrid=True,
                    gridcolor='#E5E7EB',
                    gridwidth=1,
                    showline=False,
                    zeroline=True,
                    zerolinecolor='#9CA3AF',
                    zerolinewidth=1,
                    tickfont=dict(size=11, color='#6B7280'),
                    range=[0, max_range]
                ),
                legend=dict(title='', orientation='h', y=-0.15, x=0.5, xanchor='center', font=dict(size=12)),
                margin=dict(l=60, r=40, t=60, b=70),
                height=360,
                showlegend=True,
                barmode='overlay'
            )
            
            st.plotly_chart(fig_budget, use_container_width=True)

elif st.session_state.current_page == '产量一览':
    st.markdown("""
        <style>
            .output-header {
                background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
                border-radius: 16px;
                padding: 32px;
                margin-bottom: 24px;
                box-shadow: 0 8px 32px rgba(30, 58, 95, 0.15);
            }
            .output-header-title {
                font-size: 28px;
                font-weight: 700;
                color: white;
                margin-bottom: 8px;
                letter-spacing: -0.5px;
            }
            .output-header-subtitle {
                font-size: 14px;
                color: rgba(255, 255, 255, 0.8);
                font-weight: 400;
            }
            .output-card {
                background: white;
                border-radius: 16px;
                padding: 24px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
                border: 1px solid #f1f5f9;
                transition: all 0.3s ease;
            }
            .output-card:hover {
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
                transform: translateY(-2px);
            }
            .output-card-badge {
                display: inline-block;
                padding: 6px 16px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
                margin-bottom: 16px;
            }
            .output-card-value {
                font-size: 32px;
                font-weight: 700;
                line-height: 1.2;
            }
            .output-card-label {
                font-size: 13px;
                color: #64748b;
                margin-top: 8px;
            }
            .output-section-title {
                font-size: 16px;
                font-weight: 600;
                color: #1e293b;
                margin-bottom: 16px;
                display: flex;
                align-items: center;
                gap: 8px;
            }
        </style>
        <div class='output-header'>
            <div class='output-header-title'>📊 产量一览</div>
            <div class='output-header-subtitle'>产量数据管理与趋势分析</div>
        </div>
    """, unsafe_allow_html=True)

    with st.expander('📊 上传产量数据', expanded=False):
        uploaded_file = st.file_uploader('选择Excel文件（需包含2025年产量和2026年产量工作表）', type=['xlsx', 'xls'], key='output_upload')
        
        if uploaded_file is not None:
            try:
                xls = pd.ExcelFile(uploaded_file)
                sheets = xls.sheet_names
                
                combined_df = pd.DataFrame()
                
                for sheet in sheets:
                    df = pd.read_excel(xls, sheet_name=sheet)
                    if '2025' in str(sheet):
                        df['年份'] = 2025
                    elif '2026' in str(sheet):
                        df['年份'] = 2026
                    combined_df = pd.concat([combined_df, df], ignore_index=True)
                
                st.success(f'✅ 文件上传成功！读取了 {len(sheets)} 个工作表')
                
                if 'output_data' not in st.session_state:
                    st.session_state.output_data = combined_df
                else:
                    st.session_state.output_data = pd.concat([st.session_state.output_data, combined_df], ignore_index=True)
                
                if st.button('💾 保存数据', key='save_output'):
                    save_path = '产量数据.xlsx'
                    st.session_state.output_data.to_excel(save_path, index=False)
                    st.success(f'✅ 数据已保存到 {save_path}')
            
            except Exception as e:
                st.error(f'❌ 上传失败: {str(e)}')
    
    if 'output_data' in st.session_state and not st.session_state.output_data.empty:
        df = st.session_state.output_data.copy()
        
        if '日期' in df.columns:
            df['月份'] = pd.to_datetime(df['日期']).dt.month
            df['月份'] = df['月份'].apply(lambda x: f'{x}月')
        
        st.markdown("<div class='output-section-title'>🔍 筛选器</div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            factory_filter = st.multiselect('选择工厂', df['工厂'].unique() if '工厂' in df.columns else [], key='output_factory_filter')
        
        with col2:
            month_filter = st.multiselect('选择月份', ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'], key='output_month_filter')
        
        with col3:
            focus_filter = st.multiselect('选择工作重心', df['工作重心'].unique() if '工作重心' in df.columns else [], key='output_focus_filter')
        
        filtered_df = df.copy()
        if factory_filter:
            filtered_df = filtered_df[filtered_df['工厂'].isin(factory_filter)]
        if month_filter:
            filtered_df = filtered_df[filtered_df['月份'].isin(month_filter)]
        if focus_filter:
            filtered_df = filtered_df[filtered_df['工作重心'].isin(focus_filter)]
        
        total_2026 = 0
        total_2025 = 0
        growth_rate = None
        
        production_cols = [col for col in filtered_df.columns if '产量' in col or '生产' in col or 'output' in col.lower()]
        production_col = production_cols[0] if production_cols else None
        
        if '年份' in filtered_df.columns and production_col:
            total_2026 = filtered_df[filtered_df['年份'] == 2026][production_col].sum() if not filtered_df[filtered_df['年份'] == 2026].empty else 0
            total_2025 = filtered_df[filtered_df['年份'] == 2025][production_col].sum() if not filtered_df[filtered_df['年份'] == 2025].empty else 0
            
            if total_2025 > 0:
                growth_rate = ((total_2026 - total_2025) / total_2025 * 100)
        
        st.markdown("<div class='output-section-title'>📈 产量统计</div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
                <div class='output-card'>
                    <div class='output-card-badge' style='background: linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%); color: #1D4ED8;'>2026年</div>
                    <div class='output-card-value' style='color: #1D4ED8;'>{:,}</div>
                    <div class='output-card-label'>千箱</div>
                </div>
            """.format(int(total_2026 / 1000)), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div class='output-card'>
                    <div class='output-card-badge' style='background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%); color: #D97706;'>2025年</div>
                    <div class='output-card-value' style='color: #D97706;'>{:,}</div>
                    <div class='output-card-label'>千箱</div>
                </div>
            """.format(int(total_2025 / 1000)), unsafe_allow_html=True)
        
        with col3:
            if growth_rate is not None:
                growth_color = '#059669' if growth_rate >= 0 else '#dc2626'
                growth_bg = 'linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%)' if growth_rate >= 0 else 'linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%)'
                growth_label = '↑ 同期增长' if growth_rate >= 0 else '↓ 同期下降'
                growth_display = f"{growth_rate:.2f}%"
            else:
                growth_color = '#64748b'
                growth_bg = 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)'
                growth_label = '数据不足'
                growth_display = '--'
            
            st.markdown("""
                <div class='output-card'>
                    <div class='output-card-badge' style='background: {}; color: {};'>{}</div>
                    <div class='output-card-label'>同期成长率</div>
                    <div class='output-card-value' style='color: {};'>{}</div>
                </div>
            """.format(growth_bg, growth_color, growth_label, growth_color, growth_display), unsafe_allow_html=True)
        
        st.markdown("<div class='output-section-title'>📊 产量趋势图</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            time_grain = st.selectbox('时间粒度', ['月', '周', '日', '季度'], key='output_time_grain')
        with col2:
            chart_type = st.selectbox('图表类型', ['柱形图', '折线图', '面积图', '组合图'], key='output_chart_type')
        
        import plotly.graph_objects as go
        fig_monthly = go.Figure()
        
        production_cols = [col for col in filtered_df.columns if '产量' in col or '生产' in col or 'output' in col.lower()]
        production_col = production_cols[0] if production_cols else None
        
        if '日期' in filtered_df.columns and production_col and '年份' in filtered_df.columns:
            filtered_df['日期'] = pd.to_datetime(filtered_df['日期'])
            
            if time_grain == '日':
                filtered_df['时间维度'] = filtered_df['日期'].dt.strftime('%m-%d')
                time_order = sorted(filtered_df['时间维度'].unique())
                
            elif time_grain == '周':
                filtered_df['时间维度'] = 'W' + filtered_df['日期'].dt.isocalendar().week.astype(str)
                time_order = sorted(filtered_df['时间维度'].unique())
                
            elif time_grain == '季度':
                filtered_df['时间维度'] = 'Q' + filtered_df['日期'].dt.quarter.astype(str)
                time_order = ['Q1', 'Q2', 'Q3', 'Q4']
                
            else:
                filtered_df['时间维度'] = filtered_df['日期'].dt.month.apply(lambda x: f'{x}月')
                time_order = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
            
            time_data = filtered_df.groupby(['时间维度', '年份'])[production_col].sum().unstack().fillna(0)
            time_data = time_data.reindex(time_order)
            
            if chart_type == '柱形图':
                if 2026 in time_data.columns:
                    fig_monthly.add_trace(go.Bar(
                        x=time_data.index,
                        y=time_data[2026],
                        name='26年',
                        marker_color='#0360EA',
                        marker_cornerradius=6
                    ))
                if 2025 in time_data.columns:
                    fig_monthly.add_trace(go.Bar(
                        x=time_data.index,
                        y=time_data[2025],
                        name='25年',
                        marker_color='#BDE4FC',
                        marker_cornerradius=6
                    ))
                fig_monthly.update_layout(barmode='group', bargap=0.15, bargroupgap=0.1)
                
            elif chart_type == '折线图':
                if 2026 in time_data.columns:
                    fig_monthly.add_trace(go.Scatter(
                        x=time_data.index,
                        y=time_data[2026],
                        name='26年',
                        line=dict(color='#0360EA', width=3),
                        mode='lines+markers',
                        marker=dict(size=6)
                    ))
                if 2025 in time_data.columns:
                    fig_monthly.add_trace(go.Scatter(
                        x=time_data.index,
                        y=time_data[2025],
                        name='25年',
                        line=dict(color='#BDE4FC', width=3),
                        mode='lines+markers',
                        marker=dict(size=6)
                    ))
                    
            elif chart_type == '面积图':
                if 2026 in time_data.columns:
                    fig_monthly.add_trace(go.Scatter(
                        x=time_data.index,
                        y=time_data[2026],
                        name='26年',
                        fill='tozeroy',
                        line=dict(color='#0360EA', width=2),
                        fillcolor='rgba(3, 96, 234, 0.15)'
                    ))
                if 2025 in time_data.columns:
                    fig_monthly.add_trace(go.Scatter(
                        x=time_data.index,
                        y=time_data[2025],
                        name='25年',
                        fill='tozeroy',
                        line=dict(color='#BDE4FC', width=2),
                        fillcolor='rgba(189, 228, 252, 0.3)'
                    ))
                    
            elif chart_type == '组合图':
                if 2026 in time_data.columns:
                    fig_monthly.add_trace(go.Bar(
                        x=time_data.index,
                        y=time_data[2026],
                        name='26年',
                        marker_color='#0360EA',
                        marker_cornerradius=6
                    ))
                if 2025 in time_data.columns:
                    fig_monthly.add_trace(go.Scatter(
                        x=time_data.index,
                        y=time_data[2025],
                        name='25年',
                        line=dict(color='#D97706', width=3, dash='dash'),
                        yaxis='y2',
                        mode='lines+markers',
                        marker=dict(size=6, color='#D97706')
                    ))
                fig_monthly.update_layout(barmode='group', bargap=0.15, bargroupgap=0.1,
                                        yaxis2=dict(overlaying='y', side='right'))
            
            x_label = {
                '日': '日期',
                '周': '周',
                '月': '月份',
                '季度': '季度'
            }[time_grain]
            
            fig_monthly.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title=x_label,
                yaxis_title='产量',
                legend=dict(title='', orientation='h', y=-0.15, x=0.5, xanchor='center'),
                height=350
            )
            
            st.plotly_chart(fig_monthly, use_container_width=True)
        else:
            st.markdown("<div style='text-align: center; color: #9ca3af; padding-top: 40px;'>数据中缺少必要的列（日期、产量、年份）</div>", unsafe_allow_html=True)

elif st.session_state.current_page == '营业额分析':
    st.markdown("""
        <div class='header-card'>
            <div class='header-title'>营业额分析</div>
            <div class='header-subtitle'>天津、河北行销公司数据</div>
        </div>
    """, unsafe_allow_html=True)
    
    # 初始化session_state
    if 'upload_key' not in st.session_state:
        st.session_state.upload_key = 0
    if 'upload_success' not in st.session_state:
        st.session_state.upload_success = False
    if 'upload_error' not in st.session_state:
        st.session_state.upload_error = ''
    
    # 指定数据文件
    DATA_FILE = '天津、河北行销达成.xlsx'
    
    def read_revenue_data(file_path):
        xls = pd.ExcelFile(file_path)
        sheet_names = xls.sheet_names
        # st.write(f"找到工作表: {sheet_names}")
        
        # 初始化数据
        tj_actual = {str(i) + '月': 0.0 for i in range(1, 13)}
        tj_budget = {str(i) + '月': 0.0 for i in range(1, 13)}
        hb_actual = {str(i) + '月': 0.0 for i in range(1, 13)}
        hb_budget = {str(i) + '月': 0.0 for i in range(1, 13)}
        
        for sheet in sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet)
            # st.write(f"读取工作表: {sheet}, 行数: {len(df)}, 列: {df.columns.tolist()}")
            
            # 判断是天津还是河北
            is_tianjin = '天津' in sheet
            is_hebei = '河北' in sheet
            
            if not is_tianjin and not is_hebei:
                # 如果工作表名不包含天津或河北，检查是否有公司列
                if '行销公司' in df.columns or '公司' in df.columns:
                    continue
                continue
            
            # 检查是否有日期列和预算/实际列
            if '日期' in df.columns and '预算' in df.columns and '实际' in df.columns:
                for idx, row in df.iterrows():
                    date_val = row['日期']
                    budget_val = pd.to_numeric(row['预算'], errors='coerce')
                    actual_val = pd.to_numeric(row['实际'], errors='coerce')
                    
                    # 从日期中提取月份
                    month = None
                    if pd.notna(date_val):
                        if hasattr(date_val, 'month'):
                            month = str(date_val.month) + '月'
                        else:
                            # 尝试从字符串中解析
                            date_str = str(date_val)
                            if '-' in date_str:
                                parts = date_str.split('-')
                                if len(parts) >= 2:
                                    try:
                                        month_num = int(parts[1])
                                        month = str(month_num) + '月'
                                    except:
                                        pass
                    
                    if month:
                        if is_tianjin:
                            if pd.notna(budget_val):
                                tj_budget[month] = float(budget_val)
                            if pd.notna(actual_val):
                                tj_actual[month] = float(actual_val)
                        elif is_hebei:
                            if pd.notna(budget_val):
                                hb_budget[month] = float(budget_val)
                            if pd.notna(actual_val):
                                hb_actual[month] = float(actual_val)
            else:
                st.write(f"  警告: 工作表 {sheet} 缺少日期、预算或实际列")
        
        # st.write(f"天津实际数据: {tj_actual}")
        # st.write(f"天津预算数据: {tj_budget}")
        # st.write(f"河北实际数据: {hb_actual}")
        # st.write(f"河北预算数据: {hb_budget}")
        
        return tj_actual, tj_budget, hb_actual, hb_budget
    
    # 上传数据功能和读取状态一行显示
    upload_cols = st.columns([4, 1])
    
    with upload_cols[0]:
        uploaded_file = st.file_uploader(
            '📁 上传营业额数据Excel', 
            type=['xlsx', 'xls'], 
            help='请上传包含天津、河北行销公司数据的Excel文件',
            key=f'uploader_{st.session_state.upload_key}',
            on_change=lambda: setattr(st.session_state, 'upload_triggered', True),
            label_visibility='collapsed'
        )
        
        if uploaded_file is not None:
            try:
                file_size = len(uploaded_file.getbuffer())
                if file_size == 0:
                    st.error('❌ 上传失败: 文件为空')
                    st.session_state.upload_error = '文件为空'
                else:
                    with open(DATA_FILE, 'wb') as f:
                        f.write(uploaded_file.getbuffer())
                
                    import os
                    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
                        st.success(f'✅ 数据上传成功！文件大小: {file_size/1024:.2f} KB')
                        st.session_state.upload_key += 1
                        st.session_state.upload_success = True
                        st.session_state.upload_error = ''
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error('❌ 上传失败: 文件保存后为空')
                        st.session_state.upload_error = '文件保存后为空'
            except Exception as e:
                error_msg = f'❌ 上传失败: {str(e)}'
                st.error(error_msg)
                st.session_state.upload_error = str(e)
    
    # 读取数据
    tj_actual = {}
    tj_budget = {}
    hb_actual = {}
    hb_budget = {}
    months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
    
    try:
        tj_actual, tj_budget, hb_actual, hb_budget = read_revenue_data(DATA_FILE)
        with upload_cols[1]:
            st.success("✅ 数据读取成功！")
    except Exception as e:
        with upload_cols[1]:
            st.warning(f'⚠️ 未找到数据文件')
        st.session_state.upload_error = f'文件读取失败: {str(e)}'
        tj_actual = {m: 0.0 for m in months}
        tj_budget = {m: 0.0 for m in months}
        hb_actual = {m: 0.0 for m in months}
        hb_budget = {m: 0.0 for m in months}
    
    # 行销公司筛选器
    company_filter = st.selectbox(
        '选择行销公司',
        ['全部', '天津行销', '河北行销'],
        key='revenue_company_filter'
    )
    
    # 根据筛选器确定最终数据
    if company_filter == '天津行销':
        final_tj_a, final_tj_b = tj_actual, tj_budget
        final_hb_a = {m: 0.0 for m in months}
        final_hb_b = {m: 0.0 for m in months}
    elif company_filter == '河北行销':
        final_tj_a = {m: 0.0 for m in months}
        final_tj_b = {m: 0.0 for m in months}
        final_hb_a, final_hb_b = hb_actual, hb_budget
    else:
        final_tj_a, final_tj_b = tj_actual, tj_budget
        final_hb_a, final_hb_b = hb_actual, hb_budget
    
    # 构建月度数据（实际值）
    monthly_data = pd.DataFrame({
        '公司': ['天津行销', '河北行销'],
        **{m: [final_tj_a[m], final_hb_a[m]] for m in months}
    })
    monthly_data['合计'] = monthly_data[months].sum(axis=1)
    
    # 按季度汇总
    quarter_ratios = {
        '第一季度': ['1月', '2月', '3月'],
        '第二季度': ['4月', '5月', '6月'],
        '第三季度': ['7月', '8月', '9月'],
        '第四季度': ['10月', '11月', '12月']
    }
    
    quarter_data = []
    for quarter, q_months in quarter_ratios.items():
        actual = sum(final_tj_a[m] for m in q_months) + sum(final_hb_a[m] for m in q_months)
        target = sum(final_tj_b[m] for m in q_months) + sum(final_hb_b[m] for m in q_months)
        completion = round(actual / target * 100, 1) if target > 0 else 0
        
        quarter_data.append({
            '季度': quarter,
            '目标金额': round(target / 100000, 2),
            '完成金额': round(actual / 100000, 2),
            '达成率': completion
        })
    
    # 准备图表数据 - 预算与实际对比
    chart_data = pd.DataFrame({'月份': months})
    chart_data['实际'] = [final_tj_a[m] + final_hb_a[m] for m in months]
    chart_data['预算'] = [final_tj_b[m] + final_hb_b[m] for m in months]
    
    # 季度卡片样式配置 - 轻背景重数据设计
    quarter_styles = [
        {'accent': '#3b82f6', 'tag': '#dbeafe', 'tag_text': '#1e40af'},   # 蓝色
        {'accent': '#f59e0b', 'tag': '#fef3c7', 'tag_text': '#d97706'},   # 橙色
        {'accent': '#ef4444', 'tag': '#fee2e2', 'tag_text': '#dc2626'},   # 红色
        {'accent': '#10b981', 'tag': '#d1fae5', 'tag_text': '#059669'}    # 绿色
    ]
    
    # 卡片和图表并排显示
    main_cols = st.columns([3, 5])
    
    # 左侧：4个季度卡片
    with main_cols[0]:
        card_cols = st.columns(4)
        for i, (quarter, style) in enumerate(zip(quarter_data, quarter_styles)):
            with card_cols[i]:
                rate = max(min(quarter['达成率'], 100), 0)
                half_circle_len = 100.53
                dash_array = f"{half_circle_len * rate / 100:.2f} {half_circle_len:.2f}"
                st.markdown(f"""
                    <div style='background: #F8F9FA; border-radius: 12px; padding: 20px 16px 25px 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); text-align: center; height: 312px; display: flex; flex-direction: column; position: relative; overflow: hidden;'>
                        <div style='width: 4px; height: 100%; background: {style['accent']}; position: absolute; left: 0; top: 0; border-radius: 12px 0 0 12px;'></div>
                        <div style='background: {style['tag']}; border-radius: 6px; padding: 5px 12px; text-align: center; margin-bottom: 15px;'>
                            <div style='font-size: 12px; font-weight: 600; color: {style['tag_text']};'>{quarter['季度']}</div>
                        </div>
                        <div style='flex: 1; display: flex; flex-direction: column; justify-content: flex-start;'>
                            <div style='font-size: 12px; color: #666666; margin-bottom: 4px; text-align: center;'>目标金额</div>
                            <div style='font-size: 24px; font-weight: 700; margin-bottom: 6px; text-align: center; color: {style['accent']};'>{quarter['目标金额']:.2f}<span style='font-size: 20px; font-weight: 600;'>亿</span></div>
                            <div style='font-size: 12px; color: #666666; margin-bottom: 4px; text-align: center;'>完成金额</div>
                            <div style='font-size: 24px; font-weight: 700; text-align: center; color: {style['accent']};'>{quarter['完成金额']:.2f}<span style='font-size: 20px; font-weight: 600;'>亿</span></div>
                        </div>
                        <div style='display: flex; flex-direction: column; align-items: center; margin-top: auto; padding-top: 5px;'>
                            <svg width='80' height='50' viewBox='0 0 80 50'>
                                <path d='M 8 40 A 32 32 0 0 1 72 40' stroke='#E5E7EB' stroke-width='8' fill='none' stroke-linecap='round'/>
                                <path d='M 8 40 A 32 32 0 0 1 72 40' stroke='{style['accent']}' stroke-width='8' fill='none' stroke-linecap='round' stroke-dasharray='{dash_array}' stroke-dashoffset='0'/>
                            </svg>
                            <div style='text-align: center; margin-top: -14px;'>
                                <div style='font-size: 18px; font-weight: 700; line-height: 1.2; color: {style['accent']};'>{quarter['达成率']}%</div>
                                <div style='font-size: 10px; color: #999999; line-height: 1.2;'>完成率</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    
    # 右侧：柱形图
    with main_cols[1]:
        if not chart_data.empty:
            import plotly.graph_objects as go
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=chart_data['月份'],
                y=chart_data['预算'],
                name='计划值',
                marker_color='rgba(255,255,255,0)',
                marker_line_color='#f59e0b',
                marker_line_width=2,
                marker_cornerradius=5,
                opacity=0.9
            ))
            
            fig.add_trace(go.Bar(
                x=chart_data['月份'],
                y=chart_data['实际'],
                name='实际值',
                marker_color='#3b82f6',
                marker_line_color='#1e40af',
                marker_line_width=1,
                marker_cornerradius=5,
                opacity=0.9
            ))
            
            max_budget = chart_data['预算'].max()
            max_actual = chart_data['实际'].max()
            y_max = max(max_budget, max_actual) * 1.2
            
            annotations = []
            for i, month in enumerate(months):
                actual = chart_data['实际'][i]
                budget = chart_data['预算'][i]
                diff = actual - budget
                
                if diff != 0:
                    y_pos = max(actual, budget) + y_max * 0.08
                    annotations.append(dict(
                        x=month,
                        y=y_pos,
                        text=f'{"+" if diff > 0 else ""}{int(diff):,}',
                        showarrow=False,
                        font=dict(
                            size=14,
                            color='#ef5350' if diff < 0 else '#26a69a',
                            weight='bold'
                        ),
                        xanchor='center'
                    ))
            
            fig.update_layout(
                title=dict(
                    text='预算与实际对比',
                    font=dict(size=16, weight='bold', color='#1e293b'),
                    x=0.02,
                    y=0.98,
                    xanchor='left',
                    yanchor='top'
                ),
                annotations=annotations,
                barmode='overlay',
                plot_bgcolor='#F8F9FA',
                paper_bgcolor='#F8F9FA',
                yaxis=dict(
                    title='金额（千元）',
                    showgrid=False,
                    showline=False,
                    zeroline=False,
                    automargin=True,
                    range=[0, y_max]
                ),
                xaxis=dict(
                    title='',
                    showgrid=False,
                    showline=False
                ),
                legend=dict(title='', orientation='h', y=-0.12, x=0.5, xanchor='center'),
                margin=dict(l=20, r=20, t=50, b=50),
                height=312,
                bargap=0.15,
                bargroupgap=0.1
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # 底部表格
    st.markdown('<div style="margin-top: 24px;"></div>', unsafe_allow_html=True)
    if not monthly_data.empty:
        st.markdown('<h3 style="font-size: 20px; font-weight: 600; color: #1e293b; margin-bottom: 4px;">2026年预算实际销额</h3>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 14px; color: #64748b; margin-bottom: 16px;">单位：千元</p>', unsafe_allow_html=True)
        
        # 转置并格式化表格
        table_html = '<table style="width: 100%; border-collapse: collapse; font-size: 14px; table-layout: fixed;">'
        
        # 表头 - 蓝色系渐变背景
        table_html += '<thead><tr>'
        table_html += '<th style="background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); padding: 14px 8px; text-align: center; color: white; font-weight: 600; font-size: 14px; border-radius: 4px 0 0 0; width: 8%;">公司</th>'
        months_list = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
        for m in months_list:
            table_html += f'<th style="background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); padding: 14px 4px; text-align: center; color: white; font-weight: 600; font-size: 14px; width: 6%;">{m}</th>'
        table_html += '<th style="background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); padding: 14px 8px; text-align: center; color: white; font-weight: 600; font-size: 14px; border-radius: 0 4px 0 0; width: 8%;">合计</th>'
        table_html += '</tr></thead>'
        
        # 数据行
        table_html += '<tbody>'
        row_idx = 0
        for _, row in monthly_data.iterrows():
            row_color = '#ffffff' if row_idx % 2 == 0 else '#f8fafc'
            table_html += '<tr>'
            table_html += f'<td style="background: {row_color}; padding: 14px 8px; text-align: center; font-weight: 600; color: #334155; font-size: 14px; width: 8%;">{row["公司"]}</td>'
            for m in months_list:
                val = row[m] if m in row else 0
                if isinstance(val, (int, float)):
                    display_val = f'{int(val):,}' if val > 0 else '-'
                else:
                    display_val = str(val)
                table_html += f'<td style="background: {row_color}; padding: 14px 4px; text-align: center; color: #475569; font-size: 14px; width: 6%;">{display_val}</td>'
            total_val = row['合计'] if '合计' in row else 0
            table_html += f'<td style="background: {row_color}; padding: 14px 8px; text-align: center; font-weight: 700; color: #1e293b; font-size: 14px; width: 8%;">{int(total_val):,}</td>'
            table_html += '</tr>'
            row_idx += 1
        table_html += '</tbody></table>'
        
        st.markdown(table_html, unsafe_allow_html=True)

elif st.session_state.current_page == '物料对应关系':
    import pickle
    import plotly.graph_objects as go
    
    st.markdown("""
        <div class='header-card'>
            <div class='header-title'>物料对应关系管理</div>
            <div class='header-subtitle'>管理全国通用物料与物料的对应关系</div>
        </div>
    """, unsafe_allow_html=True)

    material_cache_file = 'material_mapping_cache.pkl'
    
    if 'material_data' not in st.session_state:
        try:
            with open(material_cache_file, 'rb') as f:
                st.session_state.material_data = pickle.load(f)
        except:
            st.session_state.material_data = pd.DataFrame(columns=['全国通用物料', '物料号', '物料名称', '对应类型', '备注'])
    
    if 'new_mapping' not in st.session_state:
        st.session_state.new_mapping = {
            '全国通用物料': '',
            '物料号': '',
            '物料名称': '',
            '对应类型': '',
            '备注': ''
        }

    main_cols = st.columns([1, 1])
    
    with main_cols[0]:
        st.markdown("""
            <div style='background: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); padding: 24px;'>
                <div style='font-size: 16px; font-weight: 600; color: #1e293b; margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid #e2e8f0;'>📁 上传对应关系表</div>
            """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader('上传Excel文件', type=['xlsx', 'xls'], label_visibility='collapsed')
        if uploaded_file is not None:
            try:
                df_upload = pd.read_excel(uploaded_file)
                st.session_state.material_data = df_upload
                with open(material_cache_file, 'wb') as f:
                    pickle.dump(st.session_state.material_data, f)
                st.success('数据上传成功！')
                st.rerun()
            except Exception as e:
                st.error(f'上传失败: {str(e)}')
        
        if not st.session_state.material_data.empty:
            st.markdown(f"""
                <div style='margin-top: 16px; padding: 12px 16px; background: #f0fdf4; border-radius: 8px;'>
                    <div style='font-size: 14px; color: #16a34a;'>✓ 已加载 {len(st.session_state.material_data)} 条对应关系</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style='margin-top: 16px; padding: 12px 16px; background: #fef3c7; border-radius: 8px;'>
                    <div style='font-size: 14px; color: #d97706;'>提示：请先上传对应关系表或添加新的对应关系</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with main_cols[1]:
        st.markdown("""
            <div style='background: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); padding: 24px;'>
                <div style='font-size: 16px; font-weight: 600; color: #1e293b; margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid #e2e8f0;'>➕ 新增对应关系</div>
            """, unsafe_allow_html=True)
        
        st.session_state.new_mapping['全国通用物料'] = st.text_input('全国通用物料', st.session_state.new_mapping['全国通用物料'], label_visibility='collapsed', placeholder='如：成品-PET500*15入冰红茶柠檬味')
        st.session_state.new_mapping['物料号'] = st.text_input('物料号', st.session_state.new_mapping['物料号'], label_visibility='collapsed', placeholder='如：10012345')
        st.session_state.new_mapping['物料名称'] = st.text_input('物料名称', st.session_state.new_mapping['物料名称'], label_visibility='collapsed', placeholder='物料详细名称')
        st.session_state.new_mapping['对应类型'] = st.selectbox('对应类型', ['口味', '容量', '规格', '包装', '其他'], index=0, label_visibility='collapsed')
        st.session_state.new_mapping['备注'] = st.text_input('备注', st.session_state.new_mapping['备注'], label_visibility='collapsed', placeholder='其他说明')
        
        if st.button('添加对应关系', use_container_width=True):
            if st.session_state.new_mapping['全国通用物料'] and st.session_state.new_mapping['物料号']:
                new_row = pd.DataFrame([st.session_state.new_mapping])
                st.session_state.material_data = pd.concat([st.session_state.material_data, new_row], ignore_index=True)
                with open(material_cache_file, 'wb') as f:
                    pickle.dump(st.session_state.material_data, f)
                
                st.session_state.new_mapping = {
                    '全国通用物料': '',
                    '物料号': '',
                    '物料名称': '',
                    '对应类型': '口味',
                    '备注': ''
                }
                
                st.success('对应关系添加成功！')
                st.rerun()
            else:
                st.error('请填写全国通用物料和物料号')
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    if not st.session_state.material_data.empty:
        st.markdown("""
            <div style='background: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); padding: 24px; margin-top: 24px;'>
                <div style='font-size: 16px; font-weight: 600; color: #1e293b; margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid #e2e8f0;'>📊 对应关系统计</div>
            """, unsafe_allow_html=True)
        
        stats_cols = st.columns(4)
        with stats_cols[0]:
            total_count = len(st.session_state.material_data)
            st.markdown(f"""
                <div style='text-align: center; padding: 16px; background: #eff6ff; border-radius: 8px;'>
                    <div style='font-size: 24px; font-weight: 700; color: #3b82f6;'>{total_count}</div>
                    <div style='font-size: 12px; color: #64748b; margin-top: 4px;'>总对应关系数</div>
                </div>
            """, unsafe_allow_html=True)
        
        with stats_cols[1]:
            if '全国通用物料' in st.session_state.material_data.columns:
                unique_materials = st.session_state.material_data['全国通用物料'].nunique()
            elif len(st.session_state.material_data.columns) > 0:
                unique_materials = st.session_state.material_data.iloc[:, 0].nunique()
            else:
                unique_materials = 0
            st.markdown(f"""
                <div style='text-align: center; padding: 16px; background: #f0fdf4; border-radius: 8px;'>
                    <div style='font-size: 24px; font-weight: 700; color: #16a34a;'>{unique_materials}</div>
                    <div style='font-size: 12px; color: #64748b; margin-top: 4px;'>唯一物料数</div>
                </div>
            """, unsafe_allow_html=True)
        
        with stats_cols[2]:
            if '物料号' in st.session_state.material_data.columns:
                unique_items = st.session_state.material_data['物料号'].nunique()
            elif '物料' in st.session_state.material_data.columns:
                unique_items = st.session_state.material_data['物料'].nunique()
            else:
                unique_items = len(st.session_state.material_data)
            st.markdown(f"""
                <div style='text-align: center; padding: 16px; background: #fef3c7; border-radius: 8px;'>
                    <div style='font-size: 24px; font-weight: 700; color: #d97706;'>{unique_items}</div>
                    <div style='font-size: 12px; color: #64748b; margin-top: 4px;'>物料数</div>
                </div>
            """, unsafe_allow_html=True)
        
        with stats_cols[3]:
            if '对应类型' in st.session_state.material_data.columns:
                type_counts = st.session_state.material_data['对应类型'].value_counts().to_dict()
            elif len(st.session_state.material_data.columns) > 2:
                type_counts = st.session_state.material_data.iloc[:, 2].value_counts().to_dict()
            else:
                type_counts = {}
            st.markdown(f"""
                <div style='text-align: center; padding: 16px; background: #fce7f3; border-radius: 8px;'>
                    <div style='font-size: 24px; font-weight: 700; color: #ec4899;'>{len(type_counts)}</div>
                    <div style='font-size: 12px; color: #64748b; margin-top: 4px;'>类型数</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
                <div style='margin-top: 20px;'>
                    <div style='font-size: 14px; font-weight: 500; color: #475569; margin-bottom: 12px;'>对应类型分布</div>
                </div>
            """, unsafe_allow_html=True)
        
        if '对应类型' in st.session_state.material_data.columns:
            type_dist = st.session_state.material_data['对应类型'].value_counts()
        elif len(st.session_state.material_data.columns) > 2:
            type_dist = st.session_state.material_data.iloc[:, 2].value_counts()
        else:
            type_dist = pd.Series()
        
        type_df = pd.DataFrame({'类型': type_dist.index, '数量': type_dist.values})
        
        fig_type = go.Figure(data=[go.Bar(
            x=type_df['类型'],
            y=type_df['数量'],
            marker_color=['#3b82f6', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6'],
            marker_cornerradius=6
        )])
        
        fig_type.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            margin=dict(l=10, r=10, t=10, b=30),
            height=180,
            xaxis=dict(showgrid=False, showline=False, tickfont=dict(color='#64748b')),
            yaxis=dict(showgrid=False, showline=False, tickfont=dict(color='#64748b'))
        )
        
        st.plotly_chart(fig_type, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

# 口味深度分析模态框（放在页面末尾，确保正确覆盖整个页面）
if 'show_flavor_analysis' not in st.session_state:
    st.session_state.show_flavor_analysis = False

if st.session_state.show_flavor_analysis:
    current_flavor = st.session_state.get('flavor', '冰红茶')
    project_filter = st.session_state.get('current_analysis_project', '全部')
    product30_filter = st.session_state.get('current_analysis_product30', '全部')
    product20_filter = st.session_state.get('current_analysis_product20', '全部')
    
    has_filter = project_filter != '全部' or product30_filter != '全部' or product20_filter != '全部'
    
    if current_flavor == '全部' and not has_filter:
        st.markdown("""
            <style>
                .flavor-modal-overlay {
                    position: fixed !important;
                    top: 0 !important;
                    left: 0 !important;
                    width: 100% !important;
                    height: 100% !important;
                    background-color: rgba(0,0,0,0.5) !important;
                    display: flex !important;
                    justify-content: center !important;
                    align-items: center !important;
                    z-index: 9999 !important;
                }
                .flavor-modal-content {
                        background: white !important;
                        border-radius: 12px !important;
                        box-shadow: 0 20px 60px rgba(0,0,0,0.3) !important;
                        max-width: 600px !important;
                        width: 90% !important;
                        padding: 30px !important;
                        position: relative !important;
                    }
                </style>
                <div class="flavor-modal-overlay" id="modalOverlay" onclick="document.getElementById('closeModalBtn').click();">
                    <div class="flavor-modal-content" onclick="event.stopPropagation();">
                    <button id="closeModalBtn" style="display: none;"></button>
                    <div style="text-align: center;">
                        <div style="font-size: 48px; margin-bottom: 16px;">⚠️</div>
                        <div style="font-size: 18px; font-weight: 600; color: #374151; margin-bottom: 8px;">请先选择具体口味</div>
                        <div style="color: #64748b; font-size: 14px; margin-bottom: 20px;">请在筛选器中选择一个具体的口味后再进行达成分析</div>
                    </div>
                    <div style="text-align: center;">
        """, unsafe_allow_html=True)
        
        st.markdown("""
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button('', key='btn_closeModalBtn', use_container_width=False):
            st.session_state.show_flavor_analysis = False
            st.rerun()
    else:
        st.markdown("""
            <style>
                .flavor-modal-overlay {
                    position: fixed !important;
                    top: 0 !important;
                    left: 0 !important;
                    width: 100% !important;
                    height: 100% !important;
                    background-color: rgba(0,0,0,0.5) !important;
                    display: flex !important;
                    justify-content: center !important;
                    align-items: flex-start !important;
                    z-index: 9999 !important;
                    padding-top: 5% !important;
                }
                .flavor-modal-content {
                    background: white !important;
                    border-radius: 12px !important;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3) !important;
                    max-width: 900px !important;
                    width: 90% !important;
                    max-height: 85vh !important;
                    overflow-y: auto !important;
                    position: relative !important;
                    margin: 0 !important;
                }
            </style>
        """, unsafe_allow_html=True)
        
        project_filter = st.session_state.get('current_analysis_project', '全部')
        product30_filter = st.session_state.get('current_analysis_product30', '全部')
        product20_filter = st.session_state.get('current_analysis_product20', '全部')
        
        flavor_df = filtered_df.copy()
        
        if project_filter != '全部':
            flavor_df = flavor_df[flavor_df['口味'].isin(project_map.get(project_filter, []))]
            analysis_title = project_filter
        elif product30_filter != '全部':
            flavor_df = flavor_df[flavor_df['口味'].isin(product30_map.get(product30_filter, []))]
            analysis_title = product30_filter
        elif product20_filter != '全部':
            flavor_df = flavor_df[flavor_df['口味'].isin(product20_map.get(product20_filter, []))]
            analysis_title = product20_filter
        else:
            flavor_df = flavor_df[flavor_df['口味'] == current_flavor]
            analysis_title = current_flavor
        
        if flavor_df.empty:
            st.markdown("""
                <div class="flavor-modal-overlay">
                    <div class="flavor-modal-content">
                        <div style="padding: 24px; background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; border-radius: 12px 12px 0 0;">
                            <div style="font-size: 18px; font-weight: 600;">🍦 达成分析报告</div>
                            <div style="font-size: 12px; opacity: 0.85; margin-top: 4px;">""" + analysis_title + """ 分析</div>
                        </div>
                        <div style="padding: 24px;">
                            <div style="text-align: center; padding: 40px 20px;">
                                <div style="font-size: 48px; margin-bottom: 16px;">📊</div>
                                <div style="font-size: 18px; font-weight: 600; color: #374151; margin-bottom: 8px;">暂无分析数据</div>
                                <div style="color: #64748b; font-size: 14px;">当前筛选条件""" + analysis_title + """暂未配置分析数据</div>
                            </div>
                        </div>
                        <div style="padding: 16px 24px; border-top: 1px solid #e2e8f0; text-align: center;">
                """, unsafe_allow_html=True)
            
            if st.button('确定', key='btn_confirm_no_data_modal'):
                st.session_state.show_flavor_analysis = False
                st.rerun()
            
            st.markdown("""
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            dept_flavor_df = flavor_df.groupby('营业部').agg({
                '需求量': 'sum',
                '月累排单': 'sum',
                '预算销量': 'sum'
            }).reset_index()
            
            dept_flavor_df['需求达成率'] = dept_flavor_df.apply(lambda row: (row['月累排单'] / row['需求量']) * 100 if row['需求量'] > 0 else 0, axis=1)
            
            total_demand = dept_flavor_df['需求量'].sum()
            total_order = dept_flavor_df['月累排单'].sum()
            total_budget = dept_flavor_df['预算销量'].sum()
            
            avg_demand_rate = (total_order / total_demand) * 100 if total_demand > 0 else 0
            avg_budget_rate = (total_order / total_budget) * 100 if total_budget > 0 else 0
            
            abnormal_depts = []
            for _, row in dept_flavor_df.iterrows():
                dept_name = row['营业部']
                demand_rate = row['需求达成率']
                
                if demand_rate > 0 and demand_rate < avg_demand_rate:
                    cap_df = flavor_df[flavor_df['营业部'] == dept_name].groupby('容量').agg({
                        '需求量': 'sum',
                        '月累排单': 'sum'
                    }).reset_index()
                    
                    cap_df['差额'] = cap_df['月累排单'] - cap_df['需求量']
                    
                    max_cap = ''
                    max_diff = 0
                    for _, cap_row in cap_df.iterrows():
                        cap_diff = abs(cap_row['差额'])
                        if cap_diff > max_diff:
                            max_diff = cap_diff
                            max_cap = str(cap_row['容量']) + 'ml'
                    
                    abnormal_depts.append({
                        'name': dept_name,
                        'demandRate': demand_rate,
                        'diff': demand_rate - avg_demand_rate,
                        'maxCapacity': max_cap,
                        'maxDiff': max_diff
                    })
            
            modal_html = '<div style="position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.6);display:flex;justify-content:center;align-items:center;z-index:9999;" onclick="window.location.reload();"><div style="background:white;border-radius:12px;box-shadow:0 20px 60px rgba(0,0,0,0.3);max-width:900px;width:90%;max-height:85vh;overflow-y:auto;" onclick="event.stopPropagation();"><div style="padding: 24px; background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; border-radius: 12px 12px 0 0;"><div style="font-size: 18px; font-weight: 600;">🍦 达成分析报告</div><div style="font-size: 12px; opacity: 0.85; margin-top: 4px;">' + analysis_title + ' 分析</div></div><div style="padding: 24px;"><div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-radius: 12px; padding: 20px; margin-bottom: 24px; border: 1px solid #f59e0b;"><div style="display: flex; justify-content: space-between; align-items: center;"><div><div style="font-size: 14px; color: #92400e; font-weight: 500; margin-bottom: 4px;">🍦 分析对象</div><div style="font-size: 24px; color: #78350f; font-weight: 700;">' + analysis_title + '</div></div><div style="text-align: right; margin-right: 20px;"><div style="font-size: 14px; color: #92400e; font-weight: 500; margin-bottom: 4px;">平均需求达成率</div><div style="font-size: 32px; color: #b45309; font-weight: 700;">' + str(round(avg_demand_rate, 1)) + '%</div></div><div style="text-align: right;"><div style="font-size: 14px; color: #92400e; font-weight: 500; margin-bottom: 4px;">平均预算达成率</div><div style="font-size: 32px; color: #b45309; font-weight: 700;">' + str(round(avg_budget_rate, 1)) + '%</div></div></div></div>'

            modal_html += '<div style="font-size: 16px; font-weight: 600; color: #334155; margin-bottom: 16px; padding-left: 12px; border-left: 4px solid #3b82f6;">📊 各营业部达成率与平均指标比较</div><div style="font-size: 13px; color: #64748b; margin-bottom: 16px; padding-left: 12px;">核心分析：低于平均的营业部，需进一步拆解原因（点击数字查看容量明细）</div><div style="overflow-x: auto;"><table style="width:100%;border-collapse:collapse;border-radius:8px;overflow:hidden;margin-bottom:24px;"><thead><tr style="background-color:#f8fafc;"><th style="padding:12px 14px;text-align:left;font-size:11px;font-weight:600;color:#64748b;border-bottom:2px solid #e2e8f0;">营业部名称</th><th style="padding:12px 14px;text-align:right;font-size:11px;font-weight:600;color:#64748b;border-bottom:2px solid #e2e8f0;">排单需求达成率（%）</th><th style="padding:12px 14px;text-align:right;font-size:11px;font-weight:600;color:#64748b;border-bottom:2px solid #e2e8f0;">排单预算达成率（%）</th></tr></thead><tbody>'

            for _, row in dept_flavor_df.iterrows():
                dept_name = row['营业部']
                demand_rate = row['需求达成率']
                budget_rate = (row['月累排单'] / row['预算销量']) * 100 if row['预算销量'] > 0 else 0
                
                demand_color = '#ef4444' if demand_rate < avg_demand_rate else '#10b981'
                budget_color = '#ef4444' if budget_rate < avg_budget_rate else '#10b981'
                
                modal_html += '<tr><td style="padding:12px 14px;font-size:12px;color:#374151;border-bottom:1px solid #f1f5f9;font-weight:500;">' + dept_name + '</td><td style="padding:12px 14px;font-size:12px;border-bottom:1px solid #f1f5f9;text-align:right;font-weight:600;color:' + demand_color + ';">' + str(round(demand_rate, 1)) + '%</td><td style="padding:12px 14px;font-size:12px;border-bottom:1px solid #f1f5f9;text-align:right;font-weight:600;color:' + budget_color + ';">' + str(round(budget_rate, 1)) + '%</td></tr>'

            modal_html += '</tbody><tfoot><tr style="background-color:#f8fafc;"><td style="padding:12px 14px;font-size:12px;color:#64748b;font-weight:600;">平均值参考线</td><td style="padding:12px 14px;font-size:12px;color:#64748b;font-weight:600;text-align:right;border-top:2px solid #f59e0b;">' + str(round(avg_demand_rate, 1)) + '%</td><td style="padding:12px 14px;font-size:12px;color:#64748b;font-weight:600;text-align:right;border-top:2px solid #f59e0b;">' + str(round(avg_budget_rate, 1)) + '%</td></tr></tfoot></table></div>'
            
            modal_html += '<div style="font-size: 16px; font-weight: 600; color: #334155; margin-bottom: 16px; padding-left: 12px; border-left: 4px solid #ef4444;">📉 低于平均营业部分析</div>'

            st.markdown(modal_html, unsafe_allow_html=True)
            
            for _, row in dept_flavor_df.iterrows():
                dept_name = row['营业部']
                demand_rate = row['需求达成率']
                budget_rate = (row['月累排单'] / row['预算销量']) * 100 if row['预算销量'] > 0 else 0
                
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown('<div style="padding:12px 14px;font-size:12px;color:#64748b;">---</div>', unsafe_allow_html=True)
                with col2:
                    demand_color = '#ef4444' if demand_rate < avg_demand_rate else '#10b981'
                    if st.button(str(round(demand_rate, 1)) + '%', key=f'demand_btn_{dept_name}', use_container_width=True):
                        st.session_state['selected_dept'] = dept_name
                        st.session_state['show_capacity_detail'] = True
                with col3:
                    budget_color = '#ef4444' if budget_rate < avg_budget_rate else '#10b981'
                    if st.button(str(round(budget_rate, 1)) + '%', key=f'budget_btn_{dept_name}', use_container_width=True):
                        st.session_state['selected_dept'] = dept_name
                        st.session_state['show_capacity_detail'] = True
            
            if 'show_capacity_detail' not in st.session_state:
                st.session_state.show_capacity_detail = False
            
            if st.session_state.show_capacity_detail:
                selected_dept = st.session_state.get('selected_dept', '')
                if selected_dept:
                    dept_capacity_df = flavor_df[flavor_df['营业部'] == selected_dept].groupby('容量').agg({
                        '需求量': 'sum',
                        '月累排单': 'sum'
                    }).reset_index()
                    dept_capacity_df['差额'] = dept_capacity_df['月累排单'] - dept_capacity_df['需求量']
                    
                    st.markdown("""
                        <style>
                            .capacity-modal-overlay {
                                position: fixed !important;
                                top: 0 !important;
                                left: 0 !important;
                                width: 100% !important;
                                height: 100% !important;
                                background-color: rgba(0,0,0,0.6) !important;
                                display: flex !important;
                                justify-content: center !important;
                                align-items: center !important;
                                z-index: 10000 !important;
                                cursor: pointer !important;
                            }
                            .capacity-modal-content {
                                background: white !important;
                                border-radius: 12px !important;
                                box-shadow: 0 20px 60px rgba(0,0,0,0.3) !important;
                                max-width: 500px !important;
                                width: 90% !important;
                                max-height: 70vh !important;
                                overflow-y: auto !important;
                            }
                        </style>
                        <div class="capacity-modal-overlay" onclick="window.location.reload();">
                            <div class="capacity-modal-content" onclick="event.stopPropagation();">
                                <div style="padding: 20px; background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); color: white; border-radius: 12px 12px 0 0;">
                                    <div style="font-size: 16px; font-weight: 600;">📦 """ + selected_dept + """ - 容量明细分析</div>
                                </div>
                                <div style="padding: 20px;">
                                    <div style="overflow-x: auto;">
                                        <table style="width:100%;border-collapse:collapse;">
                                            <thead>
                                                <tr style="background-color:#f8fafc;">
                                                    <th style="padding:10px 12px;text-align:left;font-size:11px;font-weight:600;color:#64748b;border-bottom:2px solid #e2e8f0;">容量(ml)</th>
                                                    <th style="padding:10px 12px;text-align:right;font-size:11px;font-weight:600;color:#64748b;border-bottom:2px solid #e2e8f0;">需求量</th>
                                                    <th style="padding:10px 12px;text-align:right;font-size:11px;font-weight:600;color:#64748b;border-bottom:2px solid #e2e8f0;">月累排单</th>
                                                    <th style="padding:10px 12px;text-align:right;font-size:11px;font-weight:600;color:#64748b;border-bottom:2px solid #e2e8f0;">差额</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                    """, unsafe_allow_html=True)
                    
                    for _, cap_row in dept_capacity_df.iterrows():
                        capacity = cap_row['容量']
                        demand = cap_row['需求量']
                        order = cap_row['月累排单']
                        diff = cap_row['差额']
                        diff_color = '#ef4444' if diff < 0 else '#10b981'
                        sign = '-' if diff < 0 else '+'
                        
                        st.markdown("""
                                                    <tr>
                                                        <td style="padding:10px 12px;font-size:12px;color:#374151;border-bottom:1px solid #f1f5f9;">""" + str(capacity) + """ml</td>
                                                        <td style="padding:10px 12px;font-size:12px;color:#374151;border-bottom:1px solid #f1f5f9;text-align:right;">""" + str(round(demand, 2)) + """</td>
                                                        <td style="padding:10px 12px;font-size:12px;color:#374151;border-bottom:1px solid #f1f5f9;text-align:right;">""" + str(round(order, 2)) + """</td>
                                                        <td style="padding:10px 12px;font-size:12px;border-bottom:1px solid #f1f5f9;text-align:right;font-weight:600;color:""" + diff_color + """>""" + sign + str(round(abs(diff), 2)) + """</td>
                                                    </tr>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("""
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                                <div style="padding: 12px 20px; border-top: 1px solid #e2e8f0;">
                                    <button onclick="window.location.reload();" style="width: 100%; padding: 10px 24px; background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer;">关闭</button>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

            if not abnormal_depts:
                modal_html += '<div style="text-align: center; padding: 40px 20px;"><div style="font-size: 60px; margin-bottom: 20px;">✅</div><div style="font-size: 20px; font-weight: 600; color: #10b981; margin-bottom: 10px;">所有营业部均高于平均达成率，无异常</div><div style="color: #64748b; font-size: 14px;">当前筛选条件下该口味运营状况良好</div></div>'
            else:
                modal_html += '<div style="overflow-x: auto;"><table style="width:100%;border-collapse:collapse;border-radius:8px;overflow:hidden;margin-bottom:24px;"><thead><tr style="background-color:#f8fafc;"><th style="padding:12px 14px;text-align:left;font-size:11px;font-weight:600;color:#64748b;border-bottom:2px solid #e2e8f0;">营业部名称</th><th style="padding:12px 14px;text-align:left;font-size:11px;font-weight:600;color:#64748b;border-bottom:2px solid #e2e8f0;">需求达成率（%）</th><th style="padding:12px 14px;text-align:left;font-size:11px;font-weight:600;color:#64748b;border-bottom:2px solid #e2e8f0;">与平均值的差距（百分点）</th><th style="padding:12px 14px;text-align:left;font-size:11px;font-weight:600;color:#64748b;border-bottom:2px solid #e2e8f0;">差异最大的容量规格</th></tr></thead><tbody>'
                
                for dept in abnormal_depts:
                    diff_text = str(round(dept['diff'], 1))
                    capacity_info = dept['maxCapacity'] + '，差额' + str(round(dept['maxDiff'], 1)) if dept['maxDiff'] > 0 else '无有效规格差异'
                    modal_html += '<tr><td style="padding:12px 14px;font-size:12px;color:#374151;border-bottom:1px solid #f1f5f9;font-weight:500;">' + dept['name'] + '</td><td style="padding:12px 14px;font-size:12px;color:#ef4444;border-bottom:1px solid #f1f5f9;font-weight:600;">' + str(round(dept['demandRate'], 1)) + '%</td><td style="padding:12px 14px;font-size:12px;color:#ef4444;border-bottom:1px solid #f1f5f9;font-weight:600;">' + diff_text + '</td><td style="padding:12px 14px;font-size:12px;color:#374151;border-bottom:1px solid #f1f5f9;">' + capacity_info + '</td></tr>'
                
                modal_html += '</tbody></table></div>'
            
            modal_html += '</div></div></div>'
            
            st.markdown(modal_html, unsafe_allow_html=True)

elif st.session_state.current_page == '调出分析':
    html_file_path = os.path.join(os.path.dirname(__file__), '预算执行分析-天津调出-单文件版.html')
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        st.markdown("""
            <style>
            .header-title-custom {
                font-size: 20px;
                font-weight: 600;
                color: #1E293B;
            }
            .header-subtitle-custom {
                font-size: 14px;
                color: #64748b;
                margin-top: 4px;
            }
            .export-btn-area {
                display: flex;
                justify-content: center;
                padding: 20px 0;
                border-top: 1px solid #e2e8f0;
                margin-top: 16px;
            }
            .export-btn {
                background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
                color: white;
                border: none;
                padding: 12px 32px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
                transition: all 0.2s;
                display: inline-flex;
                align-items: center;
                gap: 8px;
            }
            .export-btn:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
            }
            </style>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div>
                <div class='header-title-custom'>调出分析</div>
                <div class='header-subtitle-custom'>预算执行分析 · 天津调出</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.components.v1.html(html_content, height=800, scrolling=True)
        
        st.markdown("""
            <div class='export-btn-area'>
                <button onclick="window.print()" class="export-btn">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                        <polyline points="14 2 14 8 20 8"/>
                        <line x1="16" y1="13" x2="8" y2="13"/>
                        <line x1="16" y1="17" x2="8" y2="17"/>
                        <polyline points="10 9 9 9 8 9"/>
                    </svg>
                    导出PDF
                </button>
            </div>
            <style>
            @media print {
                .export-btn-area, .stApp header, .stSidebar {
                    display: none !important;
                }
                iframe {
                    height: auto !important;
                    max-height: none !important;
                    overflow: visible !important;
                }
            }
            </style>
        """, unsafe_allow_html=True)
        
    except FileNotFoundError:
        st.error(f"文件未找到: {html_file_path}")
    except Exception as e:
        st.error(f"加载文件失败: {str(e)}")

elif st.session_state.current_page == '大修进度':
    st.markdown("""
        <div class='header-card'>
            <div class='header-title'>大修进度</div>
            <div class='header-subtitle'>生产线大修计划与进度跟踪</div>
        </div>
    """, unsafe_allow_html=True)
    
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    from datetime import datetime
    import io
    
    maintenance_data = {
        '工厂': ['TTJ2', 'TTJ1', 'TTJ1', 'TTJ2', 'TTJ1', 'TTJ2', 'TTJ2', 'TTJ2', 'TTJ2', 'TYP1', 'TYP1', 'TYP1', 'TYP1', 'TYP1', 'TYP1', 'TJPI', 'TJPI', 'TJPI', 'TJPI', 'TJPI', 'JJY1', 'JJY1', 'JJY1', 'JJY1', 'TJY1', 'TJY1'],
        '生产线名称': ['SIDEL 无菌 2011', '乐惠-保利隆', 'TBA19 (新)', 'SIDEL 无菌 2011', 'TBA19', 'SIDEL 无菌 2011', 'SIDEL无菌大小兼用线(12)', 'SIDEL 无菌 2011', 'SIDEL 无菌 2011', 'SIDEL无菌线', 'PROCOMAC38瓶口线', '彬台TBC.08大小兼用', 'SIDEL 无菌 2010', 'SIDEL CSD 40000大小兼用', '碳酸CAN线', 'KRONES矿泉水36000BPH充填1', 'KRONES矿泉水36000BPH充填2', 'KRONES矿泉水36000BPH充填3', 'KRONES矿泉水36000BPH充填4', 'KRONES矿泉水18000BPH充填5', 'PET线 SIDEL 36000BPH 07年', 'PET线 SIDEL 28000BPH 13年', 'CSD28000大小兼用', '罐线 中辰 24000CPH 18年', 'SIDEL44000线纯水充填', 'SIDEL44000线纯水充填'],
        '线别代码': ['W101', 'W303', 'W209', 'W102', 'W208', 'W103', 'W106', 'W104', 'W105', 'W111', 'W104', 'W108', 'W110', 'W112', 'W304', 'W101', 'W102', 'W103', 'W104', 'W105', 'W102', 'W103', 'W104', 'W105', 'W101', 'W102'],
        '开始时间': ['2026/12/14', '2026/09/26', '2026/09/30', '2026/09/26', '2026/09/30', '2026/08/25', '2026/09/26', '2026/10/23', '2026/11/25', '2026/10/10', '2026/11/24', '2026/10/06', '2027/01/02', '2026/09/02', '2026/09/26', '2026/12/01', '2026/12/01', '2026/11/01', '2026/10/01', '2026/11/01', '2026/11/15', '2026/12/15', '2026/10/15', '2026/09/15', '2026/10/08', '2026/12/01'],
        '结束日期': ['2027/01/27', '2026/10/18', '2026/10/15', '2026/11/09', '2026/10/15', '2026/10/08', '2026/11/09', '2026/12/06', '2027/01/08', '2026/11/24', '2027/01/09', '2026/10/21', '2027/02/16', '2026/10/08', '2026/10/18', '2026/12/25', '2026/12/25', '2026/11/25', '2026/10/25', '2026/11/25', '2026/12/15', '2026/12/15', '2026/11/15', '2026/10/15', '2026/10/31', '2026/12/31'],
        '任务完成度': ['未开始', '未开始', '未开始', '未开始', '未开始', '未开始', '未开始', '未开始', '未开始', '未开始', '未开始', '未开始', '未开始', '未开始', '未开始', '未开始', '未开始', '未开始', '未开始', '未开始', '未开始', '未开始', '未开始', '未开始', '未开始', '未开始'],
        '生产线类别': ['无菌', '热充', '无菌', '无菌', '无菌', '无菌', '无菌', '无菌', '无菌', '无菌', '无菌', '热充', '无菌', '无菌', '碳酸', '水线', '水线', '水线', '水线', '水线', '水线', '水线', '碳酸', '碳酸', '水线', '水线'],
        '产线责任人': ['张红远', '王壮', '王壮', '张红远', '王壮', '张红远', '张红远', '张红远', '张红远', '芮宇', '芮宇', '芮宇', '芮宇', '王壮', '王壮', '王亮', '王亮', '王亮', '王亮', '王亮', '王立岗', '王立岗', '王立岗', '王立岗', '杨国付', '杨国付'],
        '产线可生产品项': ['500ML全系列', 'CAN6联包，24入，礼盒', 'TP6联包&24入', '500ML&1L全系列', 'TP24入', '500ML&1L全系列', '380/550ML喝开水 366/666碱性水', '500ML全系列', '2L&1L全系列', '330&350ML茶饮500ML奶茶/全系列', '佳得乐，星巴克，贝纳颂', '900冰红&百果乐缤纷', '350ML茶饮500ML茶的传人/鲜绿绿茶/中式1L全系列', '百事碳酸', '百事', '550康水12入/24入', '550康水12入/24入', '550康水12入/24入', '550康水12入/24入', '1.5L水', '380/550喝开水12/24入', '550/1.5L康水；350/550L纯水乐', '百事碳酸', '百事碳酸', '550康水12入/24入', '550康水12入/24入']
    }
    
    df = pd.DataFrame(maintenance_data)
    df['开始时间'] = pd.to_datetime(df['开始时间'], format='%Y/%m/%d')
    df['结束日期'] = pd.to_datetime(df['结束日期'], format='%Y/%m/%d')
    df['大修天数'] = (df['结束日期'] - df['开始时间']).dt.days + 1
    
    def on_edit_change():
        edited = st.session_state.get("maintenance_editor")
        if edited is not None and not edited.empty:
            edited['开始时间'] = pd.to_datetime(edited['开始时间'])
            edited['结束日期'] = pd.to_datetime(edited['结束日期'])
            edited['大修天数'] = (edited['结束日期'] - edited['开始时间']).dt.days + 1
            
            current = st.session_state.edited_maintenance_df
            cols_to_update = ['生产线名称', '开始时间', '结束日期', '任务完成度', '大修天数']
            changed = False
            for col in cols_to_update:
                if col in edited.columns and col in current.columns:
                    if not edited[col].equals(current[col].reset_index(drop=True)):
                        changed = True
                        break
            
            if changed:
                updated = current.copy()
                for col in cols_to_update:
                    if col in edited.columns and col in updated.columns:
                        updated[col] = edited[col].values
                st.session_state.edited_maintenance_df = updated
    
    if 'edited_maintenance_df' not in st.session_state:
        st.session_state.edited_maintenance_df = df.copy()
    
    working_df = st.session_state.edited_maintenance_df.copy()
    
    total_lines = len(df)
    factory_count = df['工厂'].nunique()
    sterile_count = len(df[df['生产线类别'] == '无菌'])
    hotfill_count = len(df[df['生产线类别'] == '热充'])
    carbonic_count = len(df[df['生产线类别'] == '碳酸'])
    water_count = len(df[df['生产线类别'] == '水线'])
    
    stats_html = """
    <div style='display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; padding: 24px;'>
        <div style='background: linear-gradient(135deg, #EFF6FF 0%, #FFFFFF 100%); border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(59, 130, 246, 0.08);'>
            <div style='display: flex; align-items: center; gap: 12px;'>
                <div style='width: 44px; height: 44px; background-color: #3B82F6; border-radius: 10px; display: flex; align-items: center; justify-content: center;'>
                    <svg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='2'>
                        <rect x='3' y='3' width='18' height='18' rx='2' ry='2'/>
                        <line x1='9' y1='9' x2='15' y2='9'/>
                        <line x1='9' y1='15' x2='15' y2='15'/>
                    </svg>
                </div>
                <div>
                    <div style='font-size: 26px; font-weight: 700; color: #1e293b;'>{}</div>
                    <div style='font-size: 13px; color: #64748b;'>总检修线数</div>
                </div>
            </div>
        </div>
        <div style='background: linear-gradient(135deg, #F5F3FF 0%, #FFFFFF 100%); border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(139, 92, 246, 0.08);'>
            <div style='display: flex; align-items: center; gap: 12px;'>
                <div style='width: 44px; height: 44px; background-color: #8B5CF6; border-radius: 10px; display: flex; align-items: center; justify-content: center;'>
                    <svg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='2'>
                        <path d='M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2'/>
                        <circle cx='9' cy='7' r='4'/>
                    </svg>
                </div>
                <div>
                    <div style='font-size: 26px; font-weight: 700; color: #1e293b;'>{}</div>
                    <div style='font-size: 13px; color: #64748b;'>涉及工厂数</div>
                </div>
            </div>
        </div>
        <div style='background: linear-gradient(135deg, #ECFDF5 0%, #FFFFFF 100%); border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(16, 185, 129, 0.08);'>
            <div style='display: flex; align-items: center; gap: 12px;'>
                <div style='width: 44px; height: 44px; background-color: #10B981; border-radius: 10px; display: flex; align-items: center; justify-content: center;'>
                    <svg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='2'>
                        <polyline points='22 7 13.5 15.5 8.5 10.5 2 17'/>
                    </svg>
                </div>
                <div>
                    <div style='font-size: 26px; font-weight: 700; color: #10B981;'>{}</div>
                    <div style='font-size: 13px; color: #64748b;'>无菌线</div>
                </div>
            </div>
        </div>
        <div style='background: linear-gradient(135deg, #FFF7ED 0%, #FFFFFF 100%); border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(249, 115, 22, 0.08);'>
            <div style='display: flex; align-items: center; gap: 12px;'>
                <div style='width: 44px; height: 44px; background-color: #F97316; border-radius: 10px; display: flex; align-items: center; justify-content: center;'>
                    <svg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='2'>
                        <circle cx='12' cy='12' r='5'/>
                    </svg>
                </div>
                <div>
                    <div style='font-size: 26px; font-weight: 700; color: #F97316;'>{}</div>
                    <div style='font-size: 13px; color: #64748b;'>热充线</div>
                </div>
            </div>
        </div>
        <div style='background: linear-gradient(135deg, #F0F9FF 0%, #FFFFFF 100%); border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(14, 165, 233, 0.08);'>
            <div style='display: flex; align-items: center; gap: 12px;'>
                <div style='width: 44px; height: 44px; background-color: #0EA5E9; border-radius: 10px; display: flex; align-items: center; justify-content: center;'>
                    <svg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='2'>
                        <path d='M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z'/>
                    </svg>
                </div>
                <div>
                    <div style='font-size: 26px; font-weight: 700; color: #0EA5E9;'>{}</div>
                    <div style='font-size: 13px; color: #64748b;'>水线</div>
                </div>
            </div>
        </div>
    </div>
    """.format(total_lines, factory_count, sterile_count, hotfill_count, water_count)
    
    st.markdown(stats_html, unsafe_allow_html=True)
    
    display_df = working_df.copy()
    factory_order = {'TTJ1': 0, 'TYP1': 1, 'TTJ2': 2, 'TJPI': 3, 'JJY1': 4, 'TJY1': 5}
    display_df['工厂排序'] = working_df['工厂'].map(factory_order)
    display_df['显示名称'] = display_df['工厂'] + '-' + display_df['线别代码']
    display_df = display_df.sort_values(['工厂排序', '生产线名称'])
    
    display_df['开始时间_str'] = display_df['开始时间'].dt.strftime('%Y-%m-%d')
    display_df['结束日期_str'] = display_df['结束日期'].dt.strftime('%Y-%m-%d')
    
    fig_gantt = px.timeline(
        display_df,
        x_start="开始时间",
        x_end="结束日期",
        y="显示名称",
        color="工厂",
        text="生产线名称",
        color_discrete_map={'TTJ1': '#3B82F6', 'TYP1': '#F59E0B', 'TTJ2': '#10B981', 'TJPI': '#8B5CF6', 'JJY1': '#EC4899', 'TJY1': '#14B8A6'},
        hover_name="生产线名称",
        hover_data={
            '生产线名称': False,
            '工厂': False,
            '线别代码': False,
            '产线责任人': False,
            '任务完成度': False,
            '产线可生产品项': False,
            '开始时间_str': False,
            '结束日期_str': False
        },
        title='大修进度甘特图'
    )
    
    month_lines = []
    for month in pd.date_range(start='2026-08-01', end='2027-03-01', freq='MS'):
        month_lines.append(dict(
            type='line',
            x0=month,
            y0=0,
            x1=month,
            y1=1,
            yref='paper',
            line=dict(
                color='#E2E8F0',
                width=1,
                dash='dash'
            )
        ))
    
    row_height = 36
    total_height = max(len(display_df) * row_height + 120, 500)
    
    fig_gantt.update_layout(
        legend=dict(
            title=dict(text='工厂', font=dict(size=14, color='#64748b')),
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            visible=True
        ),
        title_font=dict(size=16, color='#1e293b'),
        xaxis_title=dict(text='时间', font=dict(size=13, color='#64748b')),
        yaxis_title=dict(text='工厂-线别代码', font=dict(size=13, color='#64748b')),
        xaxis=dict(
            tickformat='%Y-%m-%d',
            range=[pd.Timestamp('2026-08-01'), pd.Timestamp('2027-02-28')],
            gridcolor='rgba(0,0,0,0)',
            tickfont=dict(size=11, color='#64748b'),
            showgrid=True,
            gridwidth=1,
            showline=False,
            zeroline=False
        ),
        yaxis=dict(
            autorange='reversed',
            gridcolor='#f1f5f9',
            gridwidth=1,
            tickfont=dict(size=12, color='#334155', family='SF Mono, Monaco, Consolas, monospace'),
            showline=False,
            zeroline=False,
            showgrid=True
        ),
        height=total_height,
        plot_bgcolor='#ffffff',
        paper_bgcolor='#f8fafc',
        shapes=month_lines + [
            dict(
                type='line',
                x0=pd.Timestamp.today(),
                y0=0,
                x1=pd.Timestamp.today(),
                y1=1,
                yref='paper',
                line=dict(
                    color='#EF4444',
                    width=2,
                    dash='dash'
                )
            )
        ],
        annotations=[
            dict(
                x=pd.Timestamp.today(),
                y=1.02,
                xref='x',
                yref='paper',
                text='当前日期',
                showarrow=False,
                font=dict(size=12, color='#EF4444')
            )
        ],
        margin=dict(l=140, r=40, t=80, b=50)
    )
    
    fig_gantt.update_traces(
        marker=dict(
            line=dict(width=0.5, color='#ffffff'),
            opacity=0.95
        ),
        textposition='inside',
        textfont=dict(size=12, color='white', family='SF Pro Text, Helvetica, Arial, sans-serif'),
        insidetextanchor='middle',
        showlegend=True,
        customdata=display_df[['工厂', '线别代码', '产线责任人', '任务完成度', '产线可生产品项', '开始时间_str', '结束日期_str']].values,
        hovertemplate='<b>%{text}</b><br>' +
                     '工厂: %{customdata[0]}<br>' +
                     '线别代码: %{customdata[1]}<br>' +
                     '责任人: %{customdata[2]}<br>' +
                     '状态: %{customdata[3]}<br>' +
                     '可生产品项: %{customdata[4]}<br>' +
                     '开始: %{customdata[5]}<br>' +
                     '结束: %{customdata[6]}<extra></extra>'
    )
    
    st.plotly_chart(fig_gantt, use_container_width=True, config={'scrollZoom': True})
    
    import streamlit.components.v1 as components
    components.html("""
    <script>
    (function() {
        var observer = new MutationObserver(function(mutations) {
            var plots = parent.document.querySelectorAll('.js-plotly-plot');
            plots.forEach(function(plot) {
                if (!plot.__legend_modified) {
                    plot.__legend_modified = true;
                    
                    var originalOn = plot.on;
                    plot.on = function(event, callback) {
                        if (event === 'legendclick') {
                            return;
                        }
                        return originalOn.call(this, event, callback);
                    };
                    
                    var legendGroup = plot.querySelector('.legend');
                    if (legendGroup) {
                        var legendItems = legendGroup.querySelectorAll('.traces');
                        legendItems.forEach(function(item) {
                            var legendText = item.querySelector('.legendtext');
                            if (legendText) {
                                var factoryName = legendText.textContent.trim();
                                
                                item.addEventListener('click', function(e) {
                                    e.stopPropagation();
                                    e.preventDefault();
                                    e.stopImmediatePropagation();
                                    
                                    var allTraces = plot.data;
                                    var allVisible = allTraces.every(function(t) { return t.visible !== false && t.visible !== 'legendonly'; });
                                    
                                    if (allVisible) {
                                        allTraces.forEach(function(trace) {
                                            trace.visible = (trace.name === factoryName) ? true : 'legendonly';
                                        });
                                    } else {
                                        allTraces.forEach(function(trace) {
                                            trace.visible = true;
                                        });
                                    }
                                    
                                    parent.Plotly.redraw(plot);
                                    return false;
                                }, true);
                            }
                        });
                    }
                }
            });
        });
        
        observer.observe(parent.document.body, { childList: true, subtree: true });
    })();
    </script>
    """, height=0)
    
    filtered_df = working_df.copy()
    
    st.markdown('<div class="card-title">大修明细表格</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <style>
    .mtable-container {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid #E2E8F0;
    }
    .mtable {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        font-size: 14px;
    }
    .mtable thead tr {
        background: linear-gradient(135deg, #1E293B 0%, #334155 100%);
    }
    .mtable th {
        color: white;
        font-weight: 600;
        padding: 14px 16px;
        text-align: left;
        font-size: 14px;
        white-space: nowrap;
        position: relative;
    }
    .mtable th:first-child {
        border-radius: 12px 0 0 0;
    }
    .mtable th:last-child {
        border-radius: 0 12px 0 0;
    }
    .mtable th:not(:last-child)::after {
        content: '';
        position: absolute;
        right: 0;
        top: 20%;
        bottom: 20%;
        width: 1px;
        background: rgba(255,255,255,0.15);
    }
    .mtable tbody tr {
        transition: all 0.2s ease;
    }
    .mtable tbody tr:nth-child(even) {
        background-color: #F8FAFC;
    }
    .mtable tbody tr:hover {
        background-color: #F1F5F9;
        transform: scale(1.002);
    }
    .mtable td {
        padding: 14px 16px;
        border-bottom: 1px solid #E2E8F0;
        vertical-align: middle;
        white-space: nowrap;
        line-height: 1.5;
        font-size: 14px;
    }
    .mtable tbody tr:last-child td {
        border-bottom: none;
    }
    .mtable tbody tr:last-child td:first-child {
        border-radius: 0 0 0 12px;
    }
    .mtable tbody tr:last-child td:last-child {
        border-radius: 0 0 12px 0;
    }
    .mtag {
        display: inline-flex;
        align-items: center;
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 500;
        letter-spacing: 0.3px;
    }
    .mtag-status-pending {
        background: linear-gradient(135deg, #F3F4F6 0%, #E5E7EB 100%);
        color: #6B7280;
    }
    .mtag-status-inprogress {
        background: linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%);
        color: #2563EB;
    }
    .mtag-status-completed {
        background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
        color: #059669;
    }
    .mtag-category-sterile {
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        color: #2563EB;
    }
    .mtag-category-hotfill {
        background: linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 100%);
        color: #D97706;
    }
    .mtag-category-carbonate {
        background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
        color: #059669;
    }
    .mseq {
        text-align: center;
        color: #94A3B8;
        font-weight: 500;
        font-size: 14px;
    }
    .mduration {
        font-family: 'SF Mono', 'Monaco', 'Consolas', 'Roboto Mono', monospace;
        font-size: 13px;
        color: #475569;
    }
    .medit-btn {
        background: transparent;
        border: 1.5px solid #CBD5E1;
        cursor: pointer;
        padding: 6px 16px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 500;
        color: #3B82F6;
        transition: all 0.2s ease;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }
    .medit-btn:hover {
        background-color: #EFF6FF;
        border-color: #3B82F6;
        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
    }
    .medit-btn:active {
        transform: scale(0.98);
    }
    .mproduct-cell {
        max-width: 220px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        display: inline-block;
        font-size: 14px;
        color: #475569;
    }
    .mtooltip {
        position: relative;
        display: inline-block;
    }
    .mtooltip::after {
        content: attr(data-title);
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        padding: 8px 12px;
        background: #1E293B;
        color: white;
        font-size: 13px;
        border-radius: 6px;
        white-space: normal;
        max-width: 300px;
        opacity: 0;
        visibility: hidden;
        transition: all 0.2s ease;
        z-index: 1000;
        margin-bottom: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .mtooltip:hover::after {
        opacity: 1;
        visibility: visible;
    }
    </style>
    """, unsafe_allow_html=True)
    
    edit_row = st.session_state.get('edit_row', None)
    
    st.markdown("""
    <style>
    .mt-table {
        width: 100%;
        border-collapse: collapse;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .mt-table th {
        background: linear-gradient(135deg, #1E293B 0%, #334155 100%);
        color: white;
        font-weight: 600;
        padding: 14px 12px;
        font-size: 14px;
        white-space: nowrap;
        border-right: 1px solid rgba(255,255,255,0.1);
        text-align: center;
    }
    .mt-table th:last-child {
        border-right: none;
    }
    .mt-table td {
        padding: 14px 12px;
        font-size: 14px;
        white-space: nowrap;
        border-bottom: 1px solid #E2E8F0;
    }
    .mt-table tr:hover {
        background-color: #F1F5F9;
    }
    .mt-table tr:nth-child(even) {
        background-color: #F8FAFC;
    }
    .mt-seq {
        color: #94A3B8;
        font-weight: 500;
        text-align: center;
    }
    .mt-tag {
        display: inline-block;
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 500;
    }
    .mt-status-pending {
        background: linear-gradient(135deg, #F3F4F6 0%, #E5E7EB 100%);
        color: #6B7280;
    }
    .mt-status-inprogress {
        background: linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%);
        color: #2563EB;
    }
    .mt-status-completed {
        background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
        color: #059669;
    }
    .mt-category-sterile {
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        color: #2563EB;
    }
    .mt-category-hotfill {
        background: linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 100%);
        color: #D97706;
    }
    .mt-category-carbonate {
        background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
        color: #059669;
    }
    .mt-duration {
        font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
        font-size: 13px;
        color: #475569;
    }
    .mt-product {
        max-width: 200px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)
    
    factory_colors = {
        'TTJ1': {'bg': '#EFF6FF', 'border': '#3B82F6', 'text': '#1E40AF'},
        'TYP1': {'bg': '#FFF7ED', 'border': '#F59E0B', 'text': '#92400E'},
        'TTJ2': {'bg': '#ECFDF5', 'border': '#10B981', 'text': '#065F46'},
        'TJPI': {'bg': '#F5F3FF', 'border': '#8B5CF6', 'text': '#5B21B6'},
        'JJY1': {'bg': '#FDF2F8', 'border': '#EC4899', 'text': '#BE185D'},
        'TJY1': {'bg': '#F0FDFA', 'border': '#14B8A6', 'text': '#0F766E'}
    }
    
    st.markdown("""
    <style>
    .mt-factory-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 14px;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    .mt-factory-table thead tr {
        background: linear-gradient(135deg, #1E293B 0%, #334155 100%);
    }
    .mt-factory-table th {
        color: white;
        font-weight: 600;
        padding: 14px 12px;
        text-align: center;
        font-size: 14px;
        white-space: nowrap;
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    .mt-factory-table th:last-child {
        border-right: none;
    }
    .mt-factory-table tbody tr {
        transition: all 0.2s ease;
    }
    .mt-factory-table tbody tr:hover {
        filter: brightness(0.95);
        transform: scale(1.001);
    }
    .mt-factory-table td {
        padding: 12px;
        font-size: 13px;
        border-bottom: 1px solid #E2E8F0;
        white-space: nowrap;
    }
    .mt-factory-table tr:last-child td {
        border-bottom: none;
    }
    .mt-seq {
        text-align: center;
        color: #94A3B8;
        font-weight: 500;
    }
    .mt-days {
        text-align: center;
        font-weight: 600;
        font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
    }
    .mt-tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 500;
    }
    .mt-status-pending {
        background: #F3F4F6;
        color: #6B7280;
    }
    .mt-status-inprogress {
        background: #DBEAFE;
        color: #2563EB;
    }
    .mt-status-completed {
        background: #D1FAE5;
        color: #059669;
    }
    .mt-product {
        max-width: 180px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)
    
    html_table = '<table class="mt-factory-table">'
    html_table += '<thead><tr>'
    html_table += '<th style="width:50px">序号</th>'
    html_table += '<th style="width:70px">工厂</th>'
    html_table += '<th style="width:150px">生产线名称</th>'
    html_table += '<th style="width:70px">线别代码</th>'
    html_table += '<th style="width:110px">开始时间</th>'
    html_table += '<th style="width:110px">结束日期</th>'
    html_table += '<th style="width:70px">大修天数</th>'
    html_table += '<th style="width:70px">状态</th>'
    html_table += '<th style="width:60px">类别</th>'
    html_table += '<th style="width:70px">责任人</th>'
    html_table += '<th>可生产品项</th>'
    html_table += '</tr></thead><tbody>'
    
    for row_idx, (idx, row) in enumerate(filtered_df.iterrows(), 1):
        factory = row['工厂']
        colors = factory_colors.get(factory, {'bg': '#F8FAFC', 'border': '#CBD5E1', 'text': '#475569'})
        
        status_class = 'mt-status-pending' if row['任务完成度'] == '未开始' else ('mt-status-inprogress' if row['任务完成度'] == '进行中' else 'mt-status-completed')
        category_class = 'mt-status-pending' if row['生产线类别'] == '无菌' else ('mt-status-inprogress' if row['生产线类别'] == '热充' else 'mt-status-completed')
        
        start_date = row['开始时间'].strftime('%Y-%m-%d')
        end_date = row['结束日期'].strftime('%Y-%m-%d')
        days = row['大修天数']
        
        html_table += f'<tr style="background-color: {colors["bg"]}; border-left: 3px solid {colors["border"]};">'
        html_table += f'<td class="mt-seq">{row_idx}</td>'
        html_table += f'<td style="color: {colors["text"]}; font-weight: 600;">{factory}</td>'
        html_table += f'<td>{row["生产线名称"]}</td>'
        html_table += f'<td>{row["线别代码"]}</td>'
        html_table += f'<td>{start_date}</td>'
        html_table += f'<td>{end_date}</td>'
        html_table += f'<td class="mt-days" style="color: {colors["text"]};">{days}天</td>'
        html_table += f'<td style="text-align:center;"><span class="mt-tag {status_class}">{row["任务完成度"]}</span></td>'
        html_table += f'<td style="text-align:center;"><span class="mt-tag {category_class}">{row["生产线类别"]}</span></td>'
        html_table += f'<td>{row["产线责任人"]}</td>'
        html_table += f'<td><span class="mt-product" title="{row["产线可生产品项"]}">{row["产线可生产品项"]}</span></td>'
        html_table += '</tr>'
    
    html_table += '</tbody></table>'
    st.markdown(html_table, unsafe_allow_html=True)
    
    output = io.BytesIO()
    edited_df_export = working_df.copy()
    edited_df_export['开始时间'] = edited_df_export['开始时间'].dt.strftime('%Y-%m-%d')
    edited_df_export['结束日期'] = edited_df_export['结束日期'].dt.strftime('%Y-%m-%d')
    edited_df_export.to_excel(output, index=False)
    output.seek(0)
    
    st.download_button(
        label='📥 导出Excel',
        data=output,
        file_name='大修进度数据.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        use_container_width=True
    )
    
    with st.expander("✏️ 数据编辑（修改后甘特图和表格同步更新）", expanded=False):
        edit_df = working_df[['工厂', '生产线名称', '线别代码', '开始时间', '结束日期', '任务完成度', '生产线类别', '产线责任人', '产线可生产品项', '大修天数']].copy()
        edit_df['开始时间'] = edit_df['开始时间'].dt.date
        edit_df['结束日期'] = edit_df['结束日期'].dt.date
        
        edited_df = st.data_editor(
            edit_df,
            column_config={
                "工厂": st.column_config.TextColumn("工厂", disabled=True),
                "生产线名称": st.column_config.TextColumn("生产线名称"),
                "线别代码": st.column_config.TextColumn("线别代码", disabled=True),
                "开始时间": st.column_config.DateColumn("开始时间", min_value=pd.Timestamp('2026-01-01'), max_value=pd.Timestamp('2027-12-31')),
                "结束日期": st.column_config.DateColumn("结束日期", min_value=pd.Timestamp('2026-01-01'), max_value=pd.Timestamp('2027-12-31')),
                "任务完成度": st.column_config.SelectboxColumn("状态", options=["未开始", "进行中", "已完成"]),
                "生产线类别": st.column_config.TextColumn("类别", disabled=True),
                "产线责任人": st.column_config.TextColumn("责任人", disabled=True),
                "产线可生产品项": st.column_config.TextColumn("可生产品项", disabled=True, width="large"),
                "大修天数": st.column_config.NumberColumn("大修天数", disabled=True),
            },
            hide_index=True,
            num_rows="fixed",
            key="maintenance_editor",
            on_change=on_edit_change
        )