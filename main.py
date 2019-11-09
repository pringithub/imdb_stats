
from imdb import IMDb
import matplotlib.pyplot as plt
import numpy as np
import pickle
import json

PULL_FROM_API=False

class Top250:

    def __init__(self):
        self.filename = 'top250.pickle'
        self.data = []

        self.names = []
        self.years = []
        self.rating = []
        self.top_250_rank = []
        self.votes = []
        self.runtimes = []
        self.box_office = []
        #
        self.genres = []
        self.certificates = []
        self.directors = []
        #self.cast = []
        #self.writer = []

        self.get_top250_data()
        self.populate_ind_data()

    def get_top250_data(self):
        if PULL_FROM_API:
            self.data = self._retreive_and_store_top250_data_remote()
        else:
            self.data = self._retrieve_top250_data_local()
    def _retrieve_and_store_top250_data_remote(self):
        # create an instance of the IMDb class
        ia = IMDb()
        top = ia.get_top250_movies()
        for movie in top:
            print(movie["top 250 rank"])
            self.data.append( ia.get_movie(movie.movieID) )
        with open(self.filename, 'wb') as fh:
            pickle.dump(data, fh, pickle.HIGHEST_PROTOCOL)
        return data
    def _retrieve_top250_data_local(self):
        with open(self.filename, 'rb') as fh:
            return pickle.load(fh) 

    def populate_ind_data(self): 

        for movie in self.data:
            self.names.append(movie["title"])
            self.years.append(int(movie["year"]))
            self.rating.append(float(movie["rating"]))
            self.top_250_rank.append(movie["top 250 rank"])
            self.votes.append(int(movie["votes"]))
            self.runtimes.append(int(movie["runtimes"][0]))
            try: # lots of weird corner cases .. not all are in USD$, etc
                if 'box office' in movie.keys() and 'Cumulative Worldwide Gross' in (movie["box office"].keys()):
                    bo_str = movie["box office"]['Cumulative Worldwide Gross'].replace('$','').replace(',','')
                    #print(movie["title"]+': '+bo_str)
                    bo_str = bo_str.split(' ')[0] 
                    self.box_office.append(int(bo_str))
                else:
                    self.box_office.append(0) # TODO remove all with bad data
            except:
                self.box_office.append(0)

            #
            self.genres.append(movie["genres"][0]) # TODO add multiple genre support
            #self.certificates.append(movie["certificates"][0]) TODO filter out US
            self.directors.append(movie["directors"][0]["name"])


    def count_categorical(self, cat_array):
        cat_dict = {}
        for elt in cat_array:
            if elt in cat_dict:
                cat_dict[elt] += 1
            else:
                cat_dict[elt] = 1
        #
        cat = []
        num = []
        for elt in cat_dict:
            cat.append(elt)
            num.append(cat_dict[elt])
        return cat, num

    def save_scatter_plot(self, x, y, x_label, y_label, title):
        fig, ax = plt.subplots()
        ax.scatter(x,y)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(title)
        #plt.show()
        save_filename = 'results/scatter_' + x_label+'_'+y_label+'.png'
        fig.savefig(save_filename)
        plt.close(fig)

    def save_histogram_plot(self, x, x_label, y_label, title, bins=50):
        hist, bins = np.histogram(x, bins)
        width = 0.7 * (bins[1] - bins[0])
        center = (bins[:-1] + bins[1:]) / 2
        fig, ax = plt.subplots()
        ax.bar(center, hist, align='center', width=width)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(title)
        #plt.show()
        save_filename = 'results/histogram_' + x_label+'.png'
        fig.savefig(save_filename)

    def save_categorical_plot(self, x, x_label, y_label, title):
        cat, num = self.count_categorical(x)
        fig, ax = plt.subplots()
        ax.bar(cat, num)
        plt.xticks(rotation='vertical')
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(title)
        #plt.show()
        save_filename = 'results/categorical_' + x_label+'.png'
        fig.savefig(save_filename)

    def get_corr_coef(self, fields):
        #corr = np.corrcoef([years, rating, votes, runtimes])
        corr = np.corrcoef(fields)
        print(corr)
        return corr
       
# fields: names, years, rating, top_250_rank, votes, runtimes, box_office, genres, certificates, directors
if __name__=='__main__':
    t = Top250()
    # TODO add corr to title
    t.save_scatter_plot(t.years, t.rating,       'Years', 'Rating', 'Years vs Rating') 
    t.save_scatter_plot(t.years, t.top_250_rank, 'Years', 'Top 250 Rank', 'Years vs Top 250 Rank') 
    t.save_scatter_plot(t.years, t.votes,        'Years', 'Votes', 'Years vs Votes') 
    t.save_scatter_plot(t.years, t.runtimes,     'Years', 'Runtimes', 'Years vs Runtimes') 
    #t.save_scatter_plot(t.years, t.box_office,   'Years', 'Box Office ($USD)', 'Years vs Box Office ($USD)') 
    t.save_scatter_plot(t.years, t.genres,       'Years', 'Genre', 'Years vs Genre') 
    #t.save_scatter_plot(t.years, t.certificates, 'Years', 'Certificate', 'Years vs Certificate') 
    t.save_scatter_plot(t.rating, t.votes,        'Rating', 'Votes', 'Rating vs Votes') 
    t.save_scatter_plot(t.rating, t.runtimes,     'Rating', 'Runtime', 'Rating vs Runtimes') 
    #t.save_scatter_plot(t.rating, t.box_office,   'Rating', 'Box Office ($USD)', 'Rating vs Box Office ($USD)') 
    #t.save_scatter_plot(t.rating, t.certificates, 'Rating', 'Certificate', 'Rating vs Certificates') 
    #t.save_scatter_plot(t.runtimes, t.box_office, 'Runtime', 'Box Office ($USD)', 'Runtime vs Box Office ($USD)') 
    #
    t.save_histogram_plot(t.years, 'Years', 'Count', '# Top 250 binned by years')
    t.save_histogram_plot(t.rating, 'Rating', 'Count', '# Top 250 binned by rating')
    t.save_histogram_plot(t.votes, 'Votes', 'Count', '# Top 250 binned by votes')
    t.save_histogram_plot(t.runtimes, 'Runtimes', 'Count', '# Top 250 binned by runtimes')
    #t.save_histogram_plot(t.box_office, 'Box Office ($USD)', 'Count', '# Top 250 binned by box office ($USD)')
    #
    t.save_categorical_plot(t.genres, 'Genres', 'Count', '# Top 250 Movies per Genre')
    #t.save_categorical_plot(t.certificates, 'Certificates', 'Count', '# Top 250 Movies per Certificate')





