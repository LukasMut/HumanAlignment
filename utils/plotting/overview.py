import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from utils.plotting import PALETTE, metric_to_ylabel, reduce_best_final_layer
from sklearn import datasets, linear_model
import numpy as np

LEGEND_FONT_SIZE = 24
X_AXIS_FONT_SIZE = 35
Y_AXIS_FONT_SIZE = 35
TICKS_LABELSIZE = 25
MARKER_SIZE = 400
AXIS_LABELPAD = 25
xlabel = "ImageNet accuracy"
DEFAULT_SCATTER_PARAMS = dict(s=MARKER_SIZE,
                              alpha=0.9,
                              legend="full")
x_lim = [0.45, 0.92]
y_lim = [0.0, 1.0]


def overview_plot(results, network_metadata, y_metric, x_metric='imagenet_accuracy', legend_loc='upper left'):
    sns.set_context("paper")
    f = plt.figure(figsize=(14, 10), dpi=200)
    gs = f.add_gridspec(1, 1)

    sns.set_context("talk")
    with sns.axes_style("ticks"):
        f.add_subplot(gs[0, 0])
        final_layer_results = reduce_best_final_layer(results, metric=y_metric)
        df = final_layer_results.merge(network_metadata, on='model')
        df.loc[df.training.str.startswith('SSL'), 'training'] = 'Self-Supervised'
        df.imagenet_accuracy /= 100.0
        counts = df.training.value_counts()
        for name, count in zip(counts.index, counts):
            df.loc[df.training == name, 'count'] = count

        df = df.sort_values(by='count', ascending=False)

        ax = sns.scatterplot(
            data=df,
            x=x_metric,
            y=y_metric,
            hue="training",
            style="training",
            s=MARKER_SIZE,
            alpha=0.6,
            legend="full",
            hue_order=PALETTE.keys(),
            style_order=PALETTE.keys(),
            palette=PALETTE,
        )
        ax.set_ylim([y_lim[0], y_lim[1]])
        ax.yaxis.set_tick_params(labelsize=TICKS_LABELSIZE)
        ax.xaxis.set_tick_params(labelsize=TICKS_LABELSIZE)
        ax.set_ylabel(metric_to_ylabel(y_metric), fontsize=Y_AXIS_FONT_SIZE, labelpad=AXIS_LABELPAD)

        ax.set_xlabel(xlabel, fontsize=X_AXIS_FONT_SIZE, labelpad=AXIS_LABELPAD)
        ax.legend(title="", ncol=1, loc=legend_loc, fancybox=True, fontsize=17)

        regr = linear_model.LinearRegression()
        length = len(df)
        regr.fit(df.imagenet_accuracy.values.reshape((length, 1)),
                 df[y_metric].values.reshape((length, 1)))
        lims = np.array(x_lim)
        # now plot both limits against each other
        ax.plot(lims, regr.predict(np.array(lims).reshape(-1, 1)), "--", alpha=0.8, color="grey", zorder=0)
        ax.margins(x=0)
        return f
