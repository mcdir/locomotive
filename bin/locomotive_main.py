
import sys
import time
import locomotive

def display_options():
    print('Error - no command-line argument provided.')
    print('  Specify either:')
    print('    capture           - to capture the rss feeds and save them as pickled files')
    print('    classify          - to classify the pickled feed files')
    print('    classify_reuters  - classify the nltk reuters data')  
    print('    gen_cat_file      - to generate an initial training_categories.txt file from the captured feeds')
    print('    knn_simple        - demonstration of the knn algorithm with a small set of hardcoded data')
    print('    knn_rss           - knn algorithm applied to the pickled rss feed data')  
    print('    knn_reuters       - knn algorithm applied to the reuters news articles')  
    print('    recommend_by_cats - determine article related categories using other categories')
    print('  Example:')
    print('    python locomotive_main.py knn_reuters')
    
if __name__ == "__main__":
    start_time = time.time()
    if len(sys.argv) > 1:
        app = locomotive.app.Application()
        if sys.argv[1].lower()   == 'capture':
            app.capture()
        elif sys.argv[1].lower() == 'classify':
            app.classify()
        elif sys.argv[1].lower() == 'gen_cat_file':
            app.gen_cat_file()
        elif sys.argv[1].lower() == 'knn_simple':
            app.knn_simple()
        elif sys.argv[1].lower() == 'knn_rss':
            app.knn_rss() 
        elif sys.argv[1].lower() == 'knn_reuters':
            app.knn_reuters()
        elif sys.argv[1].lower() == 'classify_reuters':
            app.classify_reuters()  
        elif sys.argv[1].lower() == 'recommend_by_cats':
            app.recommend_categories_by_cats()
        else:
            display_options() 
    else:
        display_options()

    elapsed_seconds = (time.time()) - start_time 
    elapsed_minutes = float(elapsed_seconds) / float(60)
    print("Elapsed time: %f seconds, or %f minutes" % (elapsed_seconds, elapsed_minutes))
