from django.db.models import Count
from app.models import House
import matplotlib.pyplot as plt
from wordcloud import WordCloud
def wouldCloudMain_street():
    brand_counts =House.objects.values('street').annotate(count=Count('street'))
    # 构建词云数据
    wordcloud_data = {}
    for brand_count in brand_counts:
        wordcloud_data[brand_count['street']] = brand_count['count']
    # 生成词云图像
    wordcloud = WordCloud(font_path='msyh.ttc',width=800, height=800, background_color='white').generate_from_frequencies(wordcloud_data)
    # 显示词云图像
    plt.figure(figsize=(10, 10))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.savefig('static/wordcloudpic/streetcloud.jpg')
    plt.show()

def wouldCloudMain_building():
    brand_counts =House.objects.values('building').annotate(count=Count('building'))
    # 构建词云数据
    wordcloud_data = {}
    for brand_count in brand_counts:
        wordcloud_data[brand_count['building']] = brand_count['count']
    # 生成词云图像
    wordcloud = WordCloud(font_path='msyh.ttc',width=800, height=800, background_color='white').generate_from_frequencies(wordcloud_data)
    # 显示词云图像
    plt.figure(figsize=(10, 10))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.savefig('static/wordcloudpic/buildingcloud.jpg')
    plt.show()

