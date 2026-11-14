"""Sinh 7 hình báo cáo bằng số liệu catalog và sơ đồ vector có thể tái tạo.

Không sửa catalog, không tạo số liệu giả và không gọi mô hình AI. PNG dùng để
chèn Word; SVG giữ đường nét vector. Các bảng tổng hợp và checksum đi kèm để
người viết báo cáo kiểm tra được cách đếm.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from matplotlib.ticker import FuncFormatter
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from locations import region_label

GREEN='#176B50'; MID='#57987B'; PALE='#EAF3EE'; INK='#1F302D'
GRAY='#6A7474'; LIGHT='#F2F5F5'; LINE='#D0DAD6'; BLUE='#326383'
GOLD='#B58A3D'; DATE='14/11/2026'
OUTPUT=ROOT/'outputs/report_figures_20261114'
NODE_TEXTS=[]
SOURCE='Nguồn: nhóm tổng hợp từ catalog JobVista, snapshot dữ liệu 05/11/2026.'


def number(n):return f'{int(n):,}'.replace(',','.')
def pct(n,total=7050,decimals=2):return f'{n/total*100:.{decimals}f}'.replace('.',',')+'%'


def setup_fonts():
    # Arial trên Windows có đủ dấu tiếng Việt; DejaVu Sans là phương án dự phòng.
    for name in ('arial.ttf','arialbd.ttf'):
        path=Path('C:/Windows/Fonts')/name
        if path.exists():font_manager.fontManager.addfont(str(path))
    plt.rcParams.update({'font.family':'Arial' if Path('C:/Windows/Fonts/arial.ttf').exists() else 'DejaVu Sans',
        'font.size':14,'text.color':INK,'axes.labelcolor':INK,'xtick.color':GRAY,
        'ytick.color':INK,'axes.spines.top':False,'axes.spines.right':False,
        'axes.spines.left':False,'axes.spines.bottom':False,
        'svg.fonttype':'path','svg.hashsalt':'jobvista-report-20261114',
        'savefig.facecolor':'white','figure.facecolor':'white'})


def heading(fig,title,subtitle):
    fig.text(.045,.956,title,fontsize=19,fontweight='bold',va='top',color=INK)
    fig.text(.045,.918,subtitle,fontsize=12.5,va='top',color=GRAY)


def footer(fig,text=SOURCE):fig.text(.045,.027,text,fontsize=10.7,color=GRAY,va='bottom',linespacing=1.5)


def save(fig,name):
    fig.canvas.draw()
    # Kiểm tra chữ trong hộp sơ đồ không tràn, thay vì chỉ tin vào file xuất.
    renderer=fig.canvas.get_renderer()
    failures=[]
    for ax,text,bounds in NODE_TEXTS:
        if ax.figure is not fig:continue
        x,y,w,h=bounds;lo=ax.transData.transform((x,y));hi=ax.transData.transform((x+w,y+h))
        b=text.get_window_extent(renderer)
        if b.x0<lo[0]+2 or b.x1>hi[0]-2 or b.y0<lo[1]+1 or b.y1>hi[1]-1:
            failures.append(text.get_text())
    if failures:raise ValueError('Chữ vượt hộp: '+repr(failures))
    fig.savefig(OUTPUT/(name+'.png'),dpi=300)
    fig.savefig(OUTPUT/'SVG'/(name+'.svg'),metadata={'Date':'2026-11-14'})
    plt.close(fig)


def horizontal_chart(series,labels,title,subtitle,name,height):
    fig,ax=plt.subplots(figsize=(11.5,height))
    heading(fig,title,subtitle)
    fig.subplots_adjust(left=.315,right=.955,top=.866,bottom=.16)
    values=series.to_list(); positions=range(len(values))
    colors=[GREEN if i<2 else MID for i in positions]
    ax.barh(list(positions),values,height=.66,color=colors)
    ax.set_yticks(list(positions),labels=labels,fontsize=13.1)
    ax.tick_params(axis='y',length=0,pad=10)
    ax.tick_params(axis='x',length=0,pad=8,labelsize=11.5)
    ax.invert_yaxis();ax.set_axisbelow(True);ax.grid(axis='x',color='#E7ECE9',lw=.8)
    maximum=max(values);ax.set_xlim(0,maximum*1.34)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x,_:number(x)))
    ax.set_xlabel('Số tin tuyển dụng',fontsize=13,labelpad=12)
    for i,value in enumerate(values):
        ax.text(value+maximum*.018,i,f'{number(value)}  ({pct(value)})',va='center',fontsize=12.6,color=INK)
    footer(fig,SOURCE+'\nMỗi tin được đếm một lần theo trường '+('Primary_Region.' if 'khu_vuc' in name else 'Domain.'))
    save(fig,name)


def availability(jobs):
    n=len(jobs)
    exp=jobs.Experience_Known.astype(str).str.lower().eq('true')
    quantitative=jobs.Salary_Status.eq('normalized')
    negotiated=jobs.Salary_Status.isin(['negotiable','negotiable_from_source','allowance_conflict'])
    unknown=~(quantitative|negotiated)
    counts={'experience_known':int(exp.sum()),'experience_unknown':int((~exp).sum()),
            'salary_numeric':int(quantitative.sum()),'salary_negotiable':int(negotiated.sum()),
            'salary_unknown':int(unknown.sum())}
    assert counts['experience_known']+counts['experience_unknown']==n
    assert sum(counts[k] for k in ('salary_numeric','salary_negotiable','salary_unknown'))==n
    fig=plt.figure(figsize=(11.5,7.8))
    heading(fig,'Mức độ sẵn có của kinh nghiệm và tiền lương',f'Catalog {number(n)} tin • trạng thái sau chuẩn hóa dữ liệu')
    specs=[(.54,'Thông tin kinh nghiệm',[(counts['experience_known'],'Xác định số năm',GREEN),(counts['experience_unknown'],'Chưa xác định',GRAY)]),
           (.22,'Thông tin tiền lương',[(counts['salary_numeric'],'Có mức tiền',GREEN),(counts['salary_negotiable'],'Thỏa thuận / cạnh tranh',GOLD),(counts['salary_unknown'],'Chưa rõ mức lương',GRAY)])]
    for bottom,title,parts in specs:
        ax=fig.add_axes([.065,bottom,.87,.13]);left=0
        ax.set_xlim(0,100);ax.set_ylim(-.5,.5);ax.axis('off')
        fig.text(.065,bottom+.16,title,fontsize=15.5,fontweight='bold')
        for value,label,color in parts:
            share=value/n*100
            ax.barh(0,share,left=left,height=.74,color=color,edgecolor='white',linewidth=1.5)
            ax.text(left+share/2,0,f'{number(value)}\n{pct(value,n,1)}',ha='center',va='center',color='white',fontsize=13,fontweight='bold',linespacing=1.6)
            left+=share
        legend_x=.065
        widths=[.51,.40] if len(parts)==2 else [.27,.36,.28]
        for (_,label,color),width in zip(parts,widths):
            fig.patches.append(Rectangle((legend_x,bottom-.047),.012,.014,transform=fig.transFigure,facecolor=color,edgecolor='none'))
            fig.text(legend_x+.020,bottom-.046,label,fontsize=12.2,va='bottom')
            legend_x+=width
    footer(fig,SOURCE+'\n“Thỏa thuận / cạnh tranh” chưa có mức tiền cụ thể. Chưa rõ kinh nghiệm khác với 0 năm.')
    save(fig,'Hinh_3_3_Muc_do_san_co_kinh_nghiem_va_luong')
    return counts


def canvas(title,subtitle,height=9.3):
    fig=plt.figure(figsize=(11.5,height));heading(fig,title,subtitle)
    ax=fig.add_axes([.025,.07,.95,.81]);ax.set_xlim(0,100);ax.set_ylim(0,100);ax.axis('off')
    return fig,ax


def group(ax,x,y,w,h,label,fill=LIGHT,dashed=False):
    p=FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.35,rounding_size=1.2',facecolor=fill,
                    edgecolor=LINE,lw=1.2,linestyle='--' if dashed else '-',zorder=0)
    ax.add_patch(p)
    ax.text(x+2,y+h-2.8,label,fontsize=12.5,color=GRAY,fontweight='bold',va='top')


def node(ax,x,y,w,h,title,body='',fill='white',color=GREEN,size=14,title_size=14.5):
    p=FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.32,rounding_size=1',facecolor=fill,edgecolor=color,lw=1.3,zorder=3)
    ax.add_patch(p)
    if body:
        t=ax.text(x+w/2,y+h-2.2,title,ha='center',va='top',fontsize=title_size,fontweight='bold',linespacing=1.25,zorder=4)
        title_lines=title.count('\n')+1
        # Dành khoảng riêng cho tiêu đề, phần nội dung không đè lên tiêu đề.
        body_top=y+h-2.2-title_lines*3.4-1.3
        t2=ax.text(x+w/2,(y+1.7+body_top)/2,body,ha='center',va='center',fontsize=size,linespacing=1.4,zorder=4)
        NODE_TEXTS.extend([(ax,t,(x,y,w,h)),(ax,t2,(x,y,w,h))])
    else:
        t=ax.text(x+w/2,y+h/2,title,ha='center',va='center',fontsize=size,fontweight='bold',linespacing=1.4,zorder=4)
        NODE_TEXTS.append((ax,t,(x,y,w,h)))
    return (x,y,w,h)


def line(ax,points,color=GRAY,dashed=False,both=False,label=None,label_pos=None):
    for i,(a,b) in enumerate(zip(points,points[1:])):
        last=i==len(points)-2
        patch=FancyArrowPatch(a,b,arrowstyle='<->' if both and len(points)==2 else '-|>' if last else '-',
            mutation_scale=13,lw=1.35,color=color,linestyle='--' if dashed else '-',zorder=2,shrinkA=1,shrinkB=1)
        ax.add_patch(patch)
    if label and label_pos:
        ax.text(*label_pos,label,ha='center',va='center',fontsize=11.5,color=color,
                bbox={'facecolor':'white','edgecolor':'none','pad':2},zorder=5)


def architecture():
    fig,ax=canvas('Kiến trúc tổng thể của hệ thống JobVista','Web một server: trình duyệt, API Python và các kho dữ liệu có nhiệm vụ riêng.')
    node(ax,4,80,52,15,'Trình duyệt người dùng','HTML / CSS / JavaScript\nTìm việc, tải CV, xem và lưu gợi ý',fill=PALE)
    node(ax,65,80,31,15,'localStorage','CV đã đọc, lựa chọn\nViệc đã lưu, mối quan tâm',color=BLUE,size=13)
    line(ax,[(56.5,87.5),(64.5,87.5)],both=True,color=BLUE)
    group(ax,4,34,92,38,'PYTHON / FASTAPI — cổng 8000',fill='#F6F8F7')
    line(ax,[(30,79.5),(30,72.5)],both=True,label='HTTP API / JSON',label_pos=(45,76))
    node(ax,7,51,26,12,'Đọc và phân tích CV','PDF / DOCX / OCR\nKỹ năng, vị trí, số năm',size=12.9,title_size=13.2)
    node(ax,37,51,26,12,'AI Engine','TF-IDF + embeddings\nCosine, 6 điểm CV',size=13,title_size=14)
    node(ax,67,51,26,12,'Xếp hạng và giải thích','Ngưỡng, vùng, nghề\nGiảm trùng, đa dạng',size=13,title_size=13)
    line(ax,[(33.5,57),(36.5,57)]);line(ax,[(63.5,57),(66.5,57)])
    node(ax,7,38,86,10,'Cá nhân hóa và đối chiếu','Mối quan tâm tìm kiếm · Rating nhu cầu · Chuyên môn + khoảng cách (70/30)',fill=PALE,size=13,title_size=14)
    line(ax,[(80,50.5),(80,48.5)])
    node(ax,7,9,26,17,'Dữ liệu công khai','Catalog CSV 7.050 tin\nAlias, quy tắc\nTọa độ GeoNames',size=13,title_size=14)
    node(ax,37,9,26,17,'Chỉ mục truy hồi','TF-IDF trong RAM\nCache embedding\ncủa tin công khai',color=BLUE,size=13,title_size=14)
    node(ax,67,9,26,17,'SQLite runtime','Actor băm, nghề, thời gian\nRating cửa sổ 30 ngày\nKhông chứa văn bản CV',color=GOLD,size=12.8,title_size=14)
    for x in (20,50,80):line(ax,[(x,26.5),(x,33.5)])
    footer(fig,'Nguồn: tổng hợp từ web_preview.py và các module xử lý của JobVista.\nTệp CV xử lý trong RAM backend; văn bản CV đã đọc được tự lưu ở trình duyệt, tách khỏi catalog.')
    save(fig,'Hinh_3_4_Kien_truc_tong_the_JobVista')


def knowledge():
    fig,ax=canvas('Tổ chức cơ sở tri thức của hệ thống JobVista','Sơ đồ tổ chức logic của dữ liệu và quy tắc, không phải cơ sở dữ liệu đồ thị.',height=9.7)
    node(ax,26,86,48,10,'Cơ sở tri thức phục vụ gợi ý',fill=PALE,size=16)
    for x in (18,50,82):
        line(ax,[(50,85.5),(50,81),(x,81),(x,76.5)])
    node(ax,4,54,28,22,'Tin tuyển dụng','7.050 tin; 42 trường\nJob_ID, vị trí, kỹ năng\nKinh nghiệm, lương, vùng\nJD, yêu cầu, nguồn gốc',size=13.3)
    node(ax,36,54,28,22,'Từ điển và dữ kiện','Alias kỹ năng Việt / Anh\n20 nhóm nghề, lĩnh vực\nAlias khu vực\nTọa độ đại diện GeoNames',size=13.3)
    node(ax,68,54,28,22,'Quy tắc xếp hạng','6 trọng số chuyên môn\nNgưỡng, lọc nghề / vùng\nKinh nghiệm, giảm trùng\nCân bằng CV / độ gần',size=13.3)
    node(ax,4,33,92,12,'Biểu diễn truy hồi được tạo từ tin công khai','Vocabulary / IDF và ma trận TF-IDF  ·  Embedding ngữ nghĩa, cache theo checksum',fill='#EDF3F7',color=BLUE,size=13.1)
    line(ax,[(18,53.5),(18,45.5)],color=BLUE)
    group(ax,4,4,92,22,'TRẠNG THÁI CÁ NHÂN VÀ THỐNG KÊ RUNTIME — tách khỏi catalog',dashed=True)
    node(ax,7,6,41,13,'Trình duyệt','CV đã đọc, lựa chọn vùng\nViệc đã lưu và lịch sử quan tâm',color=GRAY,size=13.2)
    node(ax,52,6,41,13,'SQLite','Mã actor băm, mã nghề, thời gian\nTổng hợp rating; không lưu CV',color=GRAY,size=13.2)
    footer(fig,'Nguồn: jobs_catalog.csv, resume_profile.py, locations.py, semantic_index.py và các module xếp hạng.\n“Cơ sở tri thức” ở đây gồm dữ kiện, từ điển và quy tắc; hệ thống chưa triển khai knowledge graph.')
    save(fig,'Hinh_3_5_To_chuc_co_so_tri_thuc_JobVista')


def flow():
    fig,ax=canvas('Luồng xử lý gợi ý việc làm của JobVista','Tách luồng ghép CV và luồng gợi ý công việc tương tự.',height=11)
    group(ax,3,22,61,76,'LUỒNG GHÉP CV',fill='#F6F8F7')
    group(ax,69,22,28,76,'KHI XEM TIN',fill='#F6F8F7')
    node(ax,8,81,51,10,'1. Nhận tệp CV','PDF có chữ / scan, DOCX hoặc ảnh',size=13.2)
    node(ax,8,65,51,11,'2. Đọc và phân tích hồ sơ','Trích xuất chữ / OCR, kỹ năng, nghề, kinh nghiệm\nXác nhận nơi ở và nơi muốn làm',size=13)
    node(ax,8,45,51,15,'3. Tính điểm CV với 7.050 tin','TF-IDF + semantic + kỹ năng + vị trí\nLĩnh vực + kinh nghiệm; chuẩn hóa trọng số\nÁp ngưỡng / ý định nghề; giảm gần trùng',size=12.8)
    node(ax,8,28,23,13,'4a. Nhóm đối chiếu','Pool toàn quốc\nCân bằng 70/30\nChuyên môn / gần nhà',size=12.4,title_size=12.7)
    node(ax,36,28,23,13,'4b. Danh sách chính','Lọc nơi muốn làm\nRating khi đủ mẫu\nChưa dùng điểm 70/30',size=12.4,title_size=12.7)
    for y1,y2 in ((80.5,76.5),(64.5,60.5)):line(ax,[(33.5,y1),(33.5,y2)])
    line(ax,[(33.5,44.5),(33.5,44),(19.5,44),(19.5,41.5)])
    line(ax,[(33.5,44),(47.5,44),(47.5,41.5)])
    node(ax,72,81,22,10,'Job_ID đang xem',size=13.8)
    node(ax,72,59,22,15,'So với tin khác','Cosine TF-IDF\n+ semantic khi có\nLoại tin / nhóm trùng',size=12.3,title_size=13.2)
    node(ax,72,28,22,15,'Việc tương tự','Xếp hạng, lọc vùng\nĐa dạng công ty\nLấy top-N',size=12.5,title_size=13.5)
    line(ax,[(83,80.5),(83,74.5)]);line(ax,[(83,58.5),(83,43.5)])
    ax.text(83,50,'Dùng tin công khai\n+ chỉ mục vector',ha='center',va='center',fontsize=12.1,color=BLUE,linespacing=1.4,
            bbox={'facecolor':'#F6F8F7','edgecolor':'none','pad':5},zorder=5)
    node(ax,5,3,90,12,'5. Hiển thị kết quả và giải thích','CV: nhóm kết hợp trước, hai nhóm đối chiếu, danh sách theo vùng bên dưới\nNhấp tin để xem chi tiết; lưu việc hoặc sửa hồ sơ rồi tìm lại',fill=PALE,size=13.2,title_size=15)
    for x in (19.5,47.5,83):line(ax,[(x,27.5),(x,15.5)])
    footer(fig,'Nguồn: cv_documents.py, resume_profile.py, hybrid_recommender.py, web_preview.py, job_proximity.py.\nSemantic chưa sẵn sàng: dùng nhánh lexical có thông báo. Khoảng cách theo điểm đại diện vùng.')
    save(fig,'Hinh_3_6_Luong_xu_ly_goi_y_viec_lam')


def wireframe():
    fig,ax=canvas('Bố cục giao diện tìm việc theo CV của JobVista','Hai trạng thái kế tiếp nhau của trang CV, không hiển thị đồng thời.',height=9.7)
    for x,title in ((3,'A. Đọc và xác nhận CV'),(53,'B. Kết quả sau khi ghép CV')):
        group(ax,x,5,44,90,title,fill='#F7F9F8')
        node(ax,x+2,81,40,7,'JobVista    Khám phá · CV · Đã lưu',fill=PALE,size=11.7)
    node(ax,5,69,40,8,'01 Tải CV → 02 Xác nhận → 03 Kết quả',size=11.4,color=GRAY)
    node(ax,5,52,25,13,'Tệp CV và hồ sơ','PDF / Word / ảnh\nĐọc & phân tích CV',size=12.5,title_size=12.7)
    node(ax,33,34,12,31,'Hướng dẫn','Tải CV\n\nChọn nơi\nmuốn làm\n\nXem gợi ý',size=11.8,title_size=11.6,color=GRAY)
    node(ax,5,34,25,14,'Kiểm tra thông tin','Kỹ năng, số năm\nNơi muốn làm / nơi ở',size=12.1,title_size=12.7)
    node(ax,5,21,40,9,'Xem và sửa nội dung CV đã đọc',size=13,color=GRAY)
    node(ax,5,9,40,8,'Tìm công việc phù hợp',fill=PALE,size=14)
    node(ax,55,69,40,8,'Kết quả từ CV    ·    Chỉnh sửa CV',size=12.2)
    group(ax,55,43,40,22,'CÂN BẰNG CHUYÊN MÔN VÀ KHOẢNG CÁCH',fill=PALE)
    for i in range(3):node(ax,57+i*12.4,46,11,11,f'Gợi ý {i+1}','CV + độ gần\nĐiểm cân bằng',size=9.5,title_size=11.5)
    node(ax,55,27,19,12,'Chuyên môn nhất','Tối đa 3 tin',size=11.4,title_size=11.8)
    node(ax,77,27,18,12,'Gần nơi ở nhất','Tối đa 3 tin',size=11.4,title_size=11.8)
    group(ax,55,8,40,15,'VIỆC PHÙ HỢP CV THEO VÙNG ĐÃ CHỌN',fill='white')
    for i in range(4):node(ax,57+i*9.2,10,8,6,f'Tin {i+1}',size=11,color=GRAY)
    footer(fig,'Nguồn: tổng hợp bố cục web_ui/app.js và styles.css, phiên bản 7206ab7. Đây là sơ đồ bố cục.\nDanh sách chính: 4 thẻ / hàng trên màn hình rộng; chi tiết chỉ mở khi chọn tin, có nút đóng.')
    save(fig,'Hinh_3_7_Bo_cuc_giao_dien_tim_viec_CV')


CAPTIONS={
 'Hinh_3_1_Phan_bo_tin_theo_khu_vuc':'Hình 3.1. Biểu đồ phân bố tin tuyển dụng theo khu vực chính',
 'Hinh_3_2_Phan_bo_tin_theo_linh_vuc':'Hình 3.2. Biểu đồ phân bố tin tuyển dụng theo lĩnh vực chuyên môn',
 'Hinh_3_3_Muc_do_san_co_kinh_nghiem_va_luong':'Hình 3.3. Biểu đồ mức độ sẵn có của thông tin kinh nghiệm và tiền lương',
 'Hinh_3_4_Kien_truc_tong_the_JobVista':'Hình 3.4. Sơ đồ kiến trúc tổng thể của hệ thống JobVista',
 'Hinh_3_5_To_chuc_co_so_tri_thuc_JobVista':'Hình 3.5. Sơ đồ tổ chức cơ sở tri thức của hệ thống JobVista',
 'Hinh_3_6_Luong_xu_ly_goi_y_viec_lam':'Hình 3.6. Sơ đồ luồng xử lý gợi ý việc làm của hệ thống JobVista',
 'Hinh_3_7_Bo_cuc_giao_dien_tim_viec_CV':'Hình 3.7. Sơ đồ bố cục giao diện tìm việc theo CV của JobVista',
}


def main():
    global OUTPUT
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=OUTPUT);args=parser.parse_args();OUTPUT=args.output.resolve()
    OUTPUT.mkdir(parents=True,exist_ok=True);(OUTPUT/'SVG').mkdir(exist_ok=True);(OUTPUT/'So_lieu').mkdir(exist_ok=True)
    setup_fonts();path=ROOT/'data/jobs_catalog.csv';jobs=pd.read_csv(path).fillna('');n=len(jobs)
    manifest=json.loads((ROOT/'data/catalog_manifest.json').read_text(encoding='utf-8'))
    assert n==7050 and jobs.Job_ID.is_unique
    assert sha256(path.read_bytes()).hexdigest()==manifest['csv_sha256']
    regions=jobs.Primary_Region.value_counts();domains=jobs.Domain.value_counts()
    assert regions.sum()==domains.sum()==n
    region_labels=[region_label(code) for code in regions.index]
    horizontal_chart(regions,region_labels,'Phân bố tin tuyển dụng theo khu vực chính',
        f'{number(n)} tin tại {len(regions)} nhóm vùng • Hà Nội và TP.HCM chiếm {pct(regions.iloc[:2].sum(),n,1)}',
        'Hinh_3_1_Phan_bo_tin_theo_khu_vuc',10.8)
    horizontal_chart(domains,list(domains.index),'Phân bố tin tuyển dụng theo lĩnh vực chuyên môn',
        f'{number(n)} tin thuộc {len(domains)} lĩnh vực • nhãn lĩnh vực chuẩn hóa trong catalog',
        'Hinh_3_2_Phan_bo_tin_theo_linh_vuc',8.6)
    counts=availability(jobs);architecture();knowledge();flow();wireframe()
    for series,labels,filename,column in [(regions,region_labels,'Hinh_3_1_so_lieu.csv','Khu_vuc_chinh'),(domains,list(domains.index),'Hinh_3_2_so_lieu.csv','Linh_vuc')]:
        pd.DataFrame({column:labels,'So_tin':series.to_list(),'Ty_le_phan_tram':[round(v/n*100,6) for v in series]}).to_csv(OUTPUT/'So_lieu'/filename,index=False,encoding='utf-8-sig')
    pd.DataFrame([{'Trang_thai':k,'So_tin':v,'Ty_le_phan_tram':round(v/n*100,6)} for k,v in counts.items()]).to_csv(OUTPUT/'So_lieu/Hinh_3_3_so_lieu.csv',index=False,encoding='utf-8-sig')
    code=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    record={'generated_date':DATE,'source_csv':'data/jobs_catalog.csv','csv_sha256':manifest['csv_sha256'],'code_reference':code,
            'rows':n,'region_count':len(regions),'domain_count':len(domains),'availability':counts,'source_dataset':manifest['source_url'],
            'source_revision':manifest['revision'],'source_license':manifest['license'],'dpi':300,
            'captions':CAPTIONS,'files':{str(p.relative_to(OUTPUT)):sha256(p.read_bytes()).hexdigest() for p in OUTPUT.rglob('*') if p.suffix in ('.png','.svg','.csv')}}
    (OUTPUT/'manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    notes=['# Bộ hình Chương 3 — JobVista',f'Ngày xuất: {DATE}. Dùng số liệu catalog {number(n)} tin và mã chức năng `7206ab7` (repo đối chiếu: `{code[:7]}`).',
      '## Cách chèn vào Word','Dùng 7 file PNG ở thư mục chính: Insert → Pictures → This Device. Chọn In Line with Text, căn giữa, khóa tỷ lệ; không kéo méo ảnh. PNG 300 dpi; thư mục SVG giữ bản vector.',
      'Nên đặt chiều rộng khoảng 16–17 cm khi dùng trang A4 dọc. Hình 3.7 có hai khung nên có thể đặt trên một trang ngang rộng khoảng 22–24 cm để chữ lớn hơn. Không bật nén ảnh mạnh; có thể chọn High fidelity trong File → Options → Advanced → Image Size and Quality.',
      'Dùng Insert Caption để đánh số bên dưới. Tên/chú thích cần chèn:',*['- **'+v+'** → `'+k+'.png`' for k,v in CAPTIONS.items()],
      '## Số liệu và cách diễn giải',
      f'- Hình 3.1: mỗi Job_ID đếm một lần theo Primary_Region. Hà Nội {number(regions["ha_noi"])} và TP.HCM {number(regions["ho_chi_minh"])} tin; 24 nhóm vùng không phải danh mục hành chính đầy đủ.',
      f'- Hình 3.2: mỗi tin đếm một lần theo Domain. Có {len(domains)} lĩnh vực; không nhầm với 20 Role_Code. Lĩnh vực được chuẩn hóa bằng từ điển/quy tắc, không phải nhãn chuyên gia đã xác nhận.',
      f'- Hình 3.3: kinh nghiệm rõ {number(counts["experience_known"])} ({pct(counts["experience_known"],n,1)}), chưa rõ {number(counts["experience_unknown"])} ({pct(counts["experience_unknown"],n,1)}). Lương có mức tiền {number(counts["salary_numeric"])} ({pct(counts["salary_numeric"],n,1)}); thỏa thuận/cạnh tranh {number(counts["salary_negotiable"])} ({pct(counts["salary_negotiable"],n,1)}); chưa rõ {number(counts["salary_unknown"])} ({pct(counts["salary_unknown"],n,1)}).',
      '- Nhóm lương thỏa thuận/cạnh tranh gồm Salary_Status=negotiable, negotiable_from_source, allowance_conflict; chỉ nhóm normalized được gọi là có mức tiền. Nhóm còn lại chưa rõ. Đây là trạng thái sau làm sạch, không phải đánh giá độ đúng của nguồn.',
      '- Hình 3.4–3.6 là sơ đồ tổng hợp từ mã nguồn. Catalog ở CSV; SQLite chỉ lưu nhu cầu nghề. Cơ sở tri thức là dữ kiện, từ điển và quy tắc, chưa phải knowledge graph.',
      '- Hình 3.6 tách đối chiếu toàn quốc khỏi danh sách chính theo nơi muốn làm. Công thức cân bằng: P=1/(1+d/50); B=0,7×CV+0,3×P. Khoảng cách giữa điểm đại diện vùng, không phải đường đi. Thiếu nơi ở/tọa độ không tạo điểm cân bằng.',
      '- Hình 3.7 là wireframe hai trạng thái, không phải ảnh chụp hoặc tuyên bố cả hai trang hiện đồng thời. Chi tiết chỉ mở khi chọn tin; bản mobile tự đổi số cột.',
      '## Nguồn trích dẫn',
      '- TiniX AI — Vietnamese Job Descriptions: https://huggingface.co/datasets/tinixai/vietnamese-job-descriptions',
      '- Snapshot: https://huggingface.co/datasets/tinixai/vietnamese-job-descriptions/tree/'+manifest['revision'],
      '- Giấy phép dữ liệu CC BY-NC 4.0; tin lịch sử chưa xác minh còn tuyển. Số liệu lấy từ catalog bàn giao, không phải thống kê toàn thị trường.',
      '- Mã nguồn: https://github.com/TienMoi79/job-recommender-system/tree/'+code,
      '- Các CSV trong So_lieu và manifest.json lưu số đếm/checksum để kiểm chứng. Không dùng kết quả benchmark 500 tin làm số liệu cho 7.050 tin.',
      '## Tái tạo','Chạy `python scripts/generate_report_figures.py` từ repo, cần pandas và matplotlib. Script không sửa catalog hay dữ liệu CV.']
    (OUTPUT/'HUONG_DAN_CHEN_HINH.md').write_text('\n\n'.join(notes)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(OUTPUT),'rows':n,'domains':len(domains),'availability':counts,'png_count':len(list(OUTPUT.glob('*.png')))},ensure_ascii=False))


if __name__=='__main__':main()
