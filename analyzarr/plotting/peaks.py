
class PeakPlots(HasTraits):
    def plot_image_peaks(img_data, locations, plot_ids=False, ax=None):
        if ax is None:
            ax=plt.gca()
        ax.imshow(img_data,cmap=plt.gray(), 
                interpolation = 'nearest')
        if plot_ids:
            for pk_id in xrange(locations.shape[0]):
                plt.text(locations[pk_id,0], locations[pk_id,1], 
                         "%s"%pk_id, size=10, rotation=0.,
                         ha="center", va="center",
                         bbox = dict(boxstyle="round",
                                     ec=(1., 0.5, 0.5),
                                     fc=(1., 0.8, 0.8),
                                     )
                         )
        else:
            ax.scatter(locations[:,0],locations[:,1])
            ax.set_xlim(0,img_data.shape[0]-1)
            ax.set_ylim(img_data.shape[1]-1,0)
        return ax    
    
    def _get_pk_shifts_and_char(self, f_pc, locations, plot_shifts=False, 
                                plot_char=4, peak_id=None, comp_id=None):
        """
        Pulls out the shifts and the chosen peak characteristic (plot_char here).
        These go into the plotting routines.
        """
        if plot_shifts:
            shifts=self._get_pk_shifts(f_pc,locations,peak_id=peak_id,comp_id=comp_id)
        else: shifts=None
        if plot_char <> None:
            char=self._get_pk_char(f_pc, locations, plot_char=plot_char, peak_id=peak_id,comp_id=comp_id)
        else: char=None

        return shifts, char

    def _get_pk_shifts(self,f_pc,locations,peak_id=None,comp_id=None):
        """
        Pulls out the peak shifts
        """
        shifts=np.zeros((locations.shape[0]),dtype=[('location','f4',(1,2)),
                                                        ('shift','f4',(1,2))])
        if peak_id<>None:
            for pos in xrange(locations.shape[0]):
                shifts[pos]=(locations[pos,:2],
                           f_pc[peak_id*7+2:peak_id*7+4,pos])
        elif comp_id<>None:
            for pos in xrange(locations.shape[0]):
                shifts[pos]=(locations[pos,:2],
                             f_pc[pos*7+2:pos*7+4,comp_id])
        elif len(f_pc.shape)==1:
            for pos in xrange(locations.shape[0]):
                shifts[pos]=(locations[pos,:2],
                           f_pc[pos*7+2:pos*7+4])
        else: shifts=None
        return shifts

    def _get_pk_char(
        self,f_pc, locations, plot_char, peak_id=None, comp_id=None):
        char=np.zeros(locations.shape[0],dtype=[('location','f4',(1,2)),
                                                ('char','f4')])
        if peak_id<>None and plot_char<>None:
            # locations here is the image locations, i.e. locations of the crops.
            for pos in xrange(locations.shape[0]):
                char[pos]=(locations[pos,:2],
                           f_pc[peak_id*7+plot_char,pos])
        
        elif comp_id<>None and plot_char<>None:
            # locations is the target locations here, i.e. locations of peaks on cells.
            for pos in xrange(locations.shape[0]):
                char[pos]=(locations[pos,:2],
                           f_pc[pos*7+plot_char,comp_id])
        elif comp_id<>None:
            for pos in xrange(locations.shape[0]):
                char[pos]=(locations[pos,:2],
                           f_pc[comp_id,pos])            
        elif len(f_pc.shape)==1 and plot_char<>None:
            for pos in xrange(locations.shape[0]):
                char[pos]=(locations[pos,:2],
                           f_pc[pos*7+plot_char])
        else: char=None
        return char

    #==============================
    # MVA plotting routines
    # These grab the data to be plotted, and pass it to functions
    # in drawing/signal.py and drawing/image.py
    #=============================

    def _plot_scores_or_peak_char(
        self, s_pc, comp_ids=None, calibrate=True,
        on_peaks=False, peak_ids=None, plot_shifts=False,
        plot_char=None,
        same_window=True, comp_label=None, 
        with_factors=False, factors=None,
        cmap=plt.cm.jet, no_nans=True, per_row=3,
        quiver_color='white',vector_scale=1):
        if not hasattr(self.mapped_parameters,'locations'):
            return self._plot_scores(s_pc, comp_ids=comp_ids, 
                                     calibrate=calibrate,
                                     same_window=same_window, 
                                     comp_label=comp_label, 
                                     with_factors=with_factors, 
                                     factors=factors, cmap=cmap, 
                                     no_nans=no_nans, per_row=per_row)

        if comp_ids is None and peak_ids is None:
            peak_or_comp = 'comp'
        elif comp_ids is None and peak_ids is not None:
            peak_or_comp = 'peak'
        else:
            peak_or_comp = 'comp'
        
        if peak_ids is None and plot_char<>None:
            messages.warning('plot_char specified without peak_ids.  Must specify which peak to plot characteristics for.  Use the plot_image_peaks method to figure out which one.')
            return None

        if peak_or_comp=='comp':
            if comp_ids is None:
                comp_ids=xrange(s_pc.shape[0])

            elif not hasattr(comp_ids,'__iter__'):
                comp_ids=xrange(comp_ids)
            ids=comp_ids

        elif peak_or_comp=='peak':
            if not hasattr(peak_ids,'__iter__'):
                peak_ids=xrange(peak_ids)
            ids=peak_ids

        fig_list=[]

        smp=self.mapped_parameters
        for i in xrange(len(ids)):
            if peak_or_comp=='peak':
                fig_list.append(self._plot_image_overlay(s_pc, plot_component=None,
                           peak_id=ids[i], plot_char=plot_char, 
                           plot_shifts=plot_shifts,per_row=per_row,
                           sc_cmap=cmap,
                           quiver_color=quiver_color,
                           vector_scale=vector_scale, 
                           comp_label=comp_label))
            else:
                fig_list.append(self._plot_image_overlay(s_pc, plot_component=ids[i],
                           peak_id=None, plot_char=plot_char, 
                           plot_shifts=plot_shifts,per_row=per_row,
                           sc_cmap=cmap,
                           quiver_color=quiver_color,
                           vector_scale=vector_scale,comp_label=comp_label))
            

        if with_factors:
            return fig_list, self._plot_factors_or_pchars(factors, 
                                            comp_ids=comp_ids, 
                                            calibrate=calibrate,
                                            same_window=same_window, 
                                            comp_label=comp_label, 
                                            per_row=per_row,
                                            plot_shifts=plot_shifts,
                                            plot_char=plot_char,
                                            on_peaks=on_peaks)
        else:
            return fig_list

    def plot_pca_factors(
        self, comp_ids=6, calibrate=True,
        same_window=True, comp_label='PC', 
        on_peaks=False, img_data=None,
        plot_shifts=True, plot_char=None, 
        vector_scale=1,quiver_color='white',
        cmap=plt.cm.jet, per_row=3):
        """Plot components from PCA, either factor images or
           peak characteristics.

        Parameters
        ----------

        comp_ids : None, int, or list of ints
            if None, returns maps of all components.
            if int, returns maps of components with ids from 0 to given int.
            if list of ints, returns maps of components with ids in given list.

        calibrate : bool
            if True, calibrates plots where calibration is available from
            the axes_manager.  If False, plots are in pixels/channels.

        same_window : bool
            if True, plots each factor to the same window.  They are not scaled.
        
        comp_label : string, the label that is either the plot title (if plotting in
            separate windows) or the label in the legend (if plotting in the 
            same window)

        on_peaks : bool
            Plot peak characteristics (True), or factor images (False)

        cmap : The colormap used for the factor image, or for peak 
            characteristics, the colormap used for the scatter plot of
            some peak characteristic.
        
        per_row : int, the number of plots in each row, when the same_window
            parameter is True.

        Peak characteristic-specific functions:
        ---------------------------------------

        img_data : 2D numpy array
            If on_peaks is specified, this is the image that gets overlaid
            with the peak information. If not specified, defaults to the
            average image of your image stack.

        plot_char - None or int
        (optional, but required to plot peak characteristic overlays)
            If int, the id of the characteristic to plot as the colored 
            scatter plot.
            Possible components are:
               0 or 1: peak coordinates
               2 or 3: position difference relative to nearest target location
               4: peak height
               5: peak orientation
               6: peak eccentricity

        plot_shifts - bool, optional
            If True, plots shift overlays from the factor onto the image given in
            the cell_data parameter
        """
        factors=self._get_target(on_peaks).pc
        return self._plot_factors_or_pchars(factors, comp_ids=comp_ids, 
                                same_window=same_window, comp_label=comp_label, 
                                on_peaks=on_peaks, img_data=img_data,
                                plot_shifts=plot_shifts, plot_char=plot_char, 
                                cmap=cmap, per_row=per_row)

    def plot_ica_factors(self,comp_ids=None, calibrate=True,
                        same_window=True, comp_label='IC', 
                        on_peaks=False, img_data=None,
                        plot_shifts=True, plot_char=None, 
                        cmap=plt.cm.jet, per_row=3,
                         quiver_color='white',vector_scale=1):
        """Plot components from ICA, either factor images or
           peak characteristics.

        Parameters
        ----------

        comp_ids : None, int, or list of ints
            if None, returns maps of all components.
            if int, returns maps of components with ids from 0 to given int.
            if list of ints, returns maps of components with ids in given list.

        calibrate : bool
            if True, calibrates plots where calibration is available from
            the axes_manager.  If False, plots are in pixels/channels.

        same_window : bool
            if True, plots each factor to the same window.  They are not scaled.
        
        comp_label : string, the label that is either the plot title (if plotting in
            separate windows) or the label in the legend (if plotting in the 
            same window)

        on_peaks : bool
            Plot peak characteristics (True), or factor images (False)

        cmap : The colormap used for the factor image, or for peak 
            characteristics, the colormap used for the scatter plot of
            some peak characteristic.
        
        per_row : int, the number of plots in each row, when the same_window
            parameter is True.

        Peak characteristic-specific functions:
        ---------------------------------------

        img_data : 2D numpy array
            If on_peaks is specified, this is the image that gets overlaid
            with the peak information. If not specified, defaults to the
            average image of your image stack.

        plot_char - None or int
        (optional, but required to plot peak characteristic overlays)
            If int, the id of the characteristic to plot as the colored 
            scatter plot.
            Possible components are:
               0 or 1: peak coordinates
               2 or 3: position difference relative to nearest target location
               4: peak height
               5: peak orientation
               6: peak eccentricity

        plot_shifts - bool, optional
            If True, plots shift overlays from the factor onto the image given in
            the cell_data parameter
        """
        factors=self._get_target(on_peaks).ic
        return self._plot_factors_or_pchars(factors, comp_ids=comp_ids, 
                                same_window=same_window, comp_label=comp_label, 
                                on_peaks=on_peaks, img_data=img_data,
                                plot_shifts=plot_shifts, plot_char=plot_char, 
                                cmap=cmap, per_row=per_row)

    def plot_pca_scores(self, comp_ids=6, calibrate=True,
                       same_window=True, comp_label='PC', 
                       with_factors=False,
                       on_peaks=False, cmap=plt.cm.jet, 
                       no_nans=True,per_row=3):
        """Plot scores from PCA, either factor images or
           peak characteristics.

        Parameters
        ----------

        comp_ids : None, int, or list of ints
            if None, returns maps of all components.
            if int, returns maps of components with ids from 0 to given int.
            if list of ints, returns maps of components with ids in given list.

        calibrate : bool
            if True, calibrates plots where calibration is available from
            the axes_manager.  If False, plots are in pixels/channels.

        same_window : bool
            if True, plots each factor to the same window.  They are not scaled.
        
        comp_label : string, 
            The label that is either the plot title (if plotting in
            separate windows) or the label in the legend (if plotting in the 
            same window)

        with_factors : bool
            If True, also returns figure(s) with the factors for the
            given comp_ids.

        on_peaks : bool
            Plot scores from peak characteristics (True), 
            or factor images (False)

        cmap : matplotlib colormap
            The colormap used for the factor image, or for peak 
            characteristics, the colormap used for the scatter plot of
            some peak characteristic.
        
        no_nans : bool
            If True, removes NaN's from the score plots.

        per_row : int 
            the number of plots in each row, when the same_window
            parameter is True.
        """
        scores=self._get_target(on_peaks).v.T
        if with_factors:
            factors=self._get_target(on_peaks).pc
        else: factors=None
        return self._plot_scores_or_peak_char(scores, comp_ids=comp_ids,
                                 with_factors=with_factors, factors=factors,
                                 same_window=same_window, comp_label=comp_label,
                                 on_peaks=on_peaks, cmap=cmap,
                                 no_nans=no_nans,per_row=per_row)

    def plot_ica_scores(self, comp_ids=None, calibrate=True,
                       same_window=True, comp_label='IC', 
                       with_factors=False,
                       on_peaks=False, cmap=plt.cm.jet, 
                       no_nans=True,per_row=3):
        """Plot scores from ICA, either factor images or
           peak characteristics.

        Parameters
        ----------

        comp_ids : None, int, or list of ints
            if None, returns maps of all components.
            if int, returns maps of components with ids from 0 to given int.
            if list of ints, returns maps of components with ids in given list.

        calibrate : bool
            if True, calibrates plots where calibration is available from
            the axes_manager.  If False, plots are in pixels/channels.

        same_window : bool
            if True, plots each factor to the same window.  They are not scaled.
        
        comp_label : string, 
            The label that is either the plot title (if plotting in
            separate windows) or the label in the legend (if plotting in the 
            same window)

        with_factors : bool
            If True, also returns figure(s) with the factors for the
            given comp_ids.

        on_peaks : bool
            Plot scores from peak characteristics (True), 
            or factor images (False)

        cmap : matplotlib colormap
            The colormap used for the factor image, or for peak 
            characteristics, the colormap used for the scatter plot of
            some peak characteristic.
        
        no_nans : bool
            If True, removes NaN's from the score plots.

        per_row : int 
            the number of plots in each row, when the same_window
            parameter is True.
        """
        scores=self._get_ica_scores(self._get_target(on_peaks))
        if with_factors:
            factors=self.get_target(on_peaks).ic
        else: factors=None
        return self._plot_scores_or_peak_char(scores, comp_ids=comp_ids,
                                 with_factors=with_factors, factors=factors,
                                 same_window=same_window, comp_label=comp_label,
                                 on_peaks=on_peaks, cmap=cmap,
                                 no_nans=no_nans,per_row=per_row)

    def export_pca_results(self, comp_ids=None, 
                          factor_prefix='pc', factor_format='rpl',
                          score_prefix='PC_score', score_format='rpl', 
                          on_peaks=False,
                          quiver_color='white',
                          vector_scale=1,
                          calibrate=True, same_window=False,
                          comp_label='PC',cmap=plt.cm.jet,
                          no_nans=True,per_row=3,
                          plot_shifts=True, 
                          plot_char=None, img_data=None):
        """Export results from PCA to any of the supported formats.

        Parameters
        ----------

        comp_ids : None, int, or list of ints
            if None, returns all components/scores.
            if int, returns components/scores with ids from 0 to given int.
            if list of ints, returns components/scores with ids in given list.

        factor_prefix : string
            The prefix that any exported filenames for factors/components 
            begin with

        factor_format : string
            The extension of the format that you wish to save to.  Determines
            the kind of output.
                - For image formats (tif, png, jpg, etc.), plots are created 
                  using the plotting flags as below, and saved at 600 dpi.
                  One plot per factor is saved.
                - For multidimensional formats (rpl, hdf5), arrays are saved
                  in single files.  All factors are contained in the one
                  file.
                - For spectral formats (msa), each factor is saved to a
                  separate file.
                
        score_prefix : string
            The prefix that any exported filenames for factors/components 
            begin with

        score_format : string
            The extension of the format that you wish to save to.  Determines
            the kind of output.
                - For image formats (tif, png, jpg, etc.), plots are created 
                  using the plotting flags as below, and saved at 600 dpi.
                  One plot per score is saved.
                - For multidimensional formats (rpl, hdf5), arrays are saved
                  in single files.  All scores are contained in the one
                  file.
                - For spectral formats (msa), each score is saved to a
                  separate file.

        on_peaks : bool
            Export peak characteristics (True), or image data (False)

        Plotting options (for image file formats ONLY)
        ----------------------------------------------

        calibrate : bool
            if True, calibrates plots where calibration is available from
            the axes_manager.  If False, plots are in pixels/channels.

        same_window : bool
            if True, plots each factor to the same window.
        
        comp_label : string, the label that is either the plot title (if plotting in
            separate windows) or the label in the legend (if plotting in the 
            same window)

        cmap : The colormap used for the factor image, or for peak 
            characteristics, the colormap used for the scatter plot of
            some peak characteristic.
        
        per_row : int, the number of plots in each row, when the same_window
            parameter is True.

        Peak characteristic-specific plotting functions:
        ---------------------------------------

        img_data : 2D numpy array
            If on_peaks is specified, this is the image that gets overlaid
            with the peak information. If not specified, defaults to the
            average image of your image stack.

        plot_char - None or int
        (optional, but required to plot peak characteristic overlays)
            If int, the id of the characteristic to plot as the colored 
            scatter plot.
            Possible components are:
               0 or 1: peak coordinates
               2 or 3: position difference relative to nearest target location
               4: peak height
               5: peak orientation
               6: peak eccentricity

        plot_shifts - bool, optional
            If True, plots shift overlays from the factor onto the image given in
            the cell_data parameter
        """
        factors=self._get_target(on_peaks).pc
        scores=self._get_target(on_peaks).v.T
        self._export_factors(factors, comp_ids=comp_ids,
                             calibrate=calibrate,
                             plot_shifts=plot_shifts,
                             plot_char=plot_char,
                             img_data=img_data,
                             factor_prefix=factor_prefix,
                             factor_format=factor_format,
                             comp_label=comp_label,
                             on_peaks=on_peaks,
                             quiver_color=quiver_color,
                             vector_scale=vector_scale,
                             cmap=cmap,
                             no_nans=no_nans,
                             same_window=same_window,
                             per_row=per_row)
        self._export_scores(scores,comp_ids=comp_ids,
                            calibrate=calibrate,
                            score_prefix=score_prefix,
                            score_format=score_format,
                            comp_label=comp_label,
                            cmap=cmap,
                            same_window=same_window,
                            no_nans=no_nans,
                            per_row=per_row)

    def export_ica_results(self, comp_ids=None, 
                          factor_prefix='ic', factor_format='rpl',
                          score_prefix='IC_score', score_format='rpl', 
                          on_peaks=False,
                          calibrate=True, same_window=False,
                          comp_label='IC',cmap=plt.cm.jet,
                          no_nans=True,per_row=3,
                          plot_shifts=True, 
                          quiver_color='white',vector_scale=1,
                          plot_char=None, img_data=None):
        """Export results from ICA to any of the supported formats.

        Parameters
        ----------

        comp_ids : None, int, or list of ints
            if None, returns all components/scores.
            if int, returns components/scores with ids from 0 to given int.
            if list of ints, returns components/scores with ids in given list.

        factor_prefix : string
            The prefix that any exported filenames for factors/components 
            begin with

        factor_format : string
            The extension of the format that you wish to save to.  Determines
            the kind of output.
                - For image formats (tif, png, jpg, etc.), plots are created 
                  using the plotting flags as below, and saved at 600 dpi.
                  One plot per factor is saved.
                - For multidimensional formats (rpl, hdf5), arrays are saved
                  in single files.  All factors are contained in the one
                  file.
                - For spectral formats (msa), each factor is saved to a
                  separate file.
                
        score_prefix : string
            The prefix that any exported filenames for factors/components 
            begin with

        score_format : string
            The extension of the format that you wish to save to.  Determines
            the kind of output.
                - For image formats (tif, png, jpg, etc.), plots are created 
                  using the plotting flags as below, and saved at 600 dpi.
                  One plot per score is saved.
                - For multidimensional formats (rpl, hdf5), arrays are saved
                  in single files.  All scores are contained in the one
                  file.
                - For spectral formats (msa), each score is saved to a
                  separate file.

        on_peaks : bool
            Export peak characteristics (True), or image data (False)

        Plotting options (for image file formats ONLY)
        ----------------------------------------------

        calibrate : bool
            if True, calibrates plots where calibration is available from
            the axes_manager.  If False, plots are in pixels/channels.

        same_window : bool
            if True, plots each factor to the same window.
        
        comp_label : string, the label that is either the plot title (if plotting in
            separate windows) or the label in the legend (if plotting in the 
            same window)

        cmap : The colormap used for the factor image, or for peak 
            characteristics, the colormap used for the scatter plot of
            some peak characteristic.
        
        per_row : int, the number of plots in each row, when the same_window
            parameter is True.

        Peak characteristic-specific plotting functions:
        ---------------------------------------

        img_data : 2D numpy array
            If on_peaks is specified, this is the image that gets overlaid
            with the peak information. If not specified, defaults to the
            average image of your image stack.

        plot_char - None or int
        (optional, but required to plot peak characteristic overlays)
            If int, the id of the characteristic to plot as the colored 
            scatter plot.
            Possible components are:
               0 or 1: peak coordinates
               2 or 3: position difference relative to nearest target location
               4: peak height
               5: peak orientation
               6: peak eccentricity

        plot_shifts - bool, optional
            If True, plots shift overlays from the factor onto the image given in
            the cell_data parameter
        """
        factors=self._get_target(on_peaks).ic
        scores=self._get_ica_scores(self._get_target(on_peaks))
        self._export_factors(factors, comp_ids=comp_ids,
                             calibrate=calibrate,
                             plot_shifts=plot_shifts,
                             plot_char=plot_char,
                             img_data=img_data,
                             factor_prefix=factor_prefix,
                             factor_format=factor_format,
                             comp_label=comp_label,
                             on_peaks=on_peaks,
                             quiver_color=quiver_color,
                             vector_scale=vector_scale,
                             cmap=cmap,
                             no_nans=no_nans,
                             same_window=same_window,
                             per_row=per_row)
        self._export_scores(scores,comp_ids=comp_ids,
                            calibrate=calibrate,
                            score_prefix=score_prefix,
                            score_format=score_format,
                            comp_label=comp_label,
                            cmap=cmap,
                            same_window=same_window,
                            no_nans=no_nans,
                            per_row=per_row)

    def plot_image_peaks(self,img_data=None, locations=None, peak_width=10, 
                         subpixel=False, medfilt_radius=5, plot_ids=True):
        """Overlay an image with a scatter map of peak locations.

        Parameters:
        -----------
        img_data : None or 2D numpy array
            If None, uses the average image (for stacks), or just
            the image (for 2D images)
        locations : None or nx2 numpy array
            If None, function locates peaks on img_data using parameters
            below.
        plot_ids : bool
            If True, plots the peak id instead of a simple scatter map.
            Use this function to identify a peak to overlay a characteristic of
            onto the original experimental image using the plot_image_overlay
            function.

        Peak locator parameters:
        ------------------------
        peak_width : int
            The width of peaks to be found
         
        subpixel : bool
            If True, finds the subpixel center of mass of peaks
            If False, finds the index at which the peak max occurs.

        medfilt_radius : int or None
            If int, the radius of a median filter applied to the image
            prior to peak finding.  NOTE: must be an odd number.
            If None, no median filter is applied.
        """
        if img_data==None:
            if len(self.data.shape)>2:
                img_data=np.average(self.data,axis=0)
            else:
                img_data=self.data
            if locations==None and hasattr(self.mapped_parameters,
                                           'target_locations'):
                locations=self.mapped_parameters.target_locations
        if locations==None:
            locations=pc.two_dim_peakfind(img_data, subpixel=subpixel,
                                  peak_width=peak_width, 
                                  medfilt_radius=medfilt_radius)
        return imgdraw.plot_image_peaks(img_data, locations, plot_ids)

    def _plot_image_overlay(self,f_pc, plot_component=None,
                           peak_id=None, plot_char=None, 
                           plot_shifts=False,calibrate=True,
                            img_cmap=plt.cm.gray,
                            sc_cmap=plt.cm.jet,
                            quiver_color='white',vector_scale=1,
                            per_row=3,same_window=True,
                            comp_label=None):
        """Overlays scores or some peak characteristic on top of an image
        plot of the original experimental image.  Useful for obtaining a 
        bird's-eye view of some image characteristic.

        plot_component - None or int 
        (optional, but required to plot score overlays)
            The integer index of the component to plot scores for.
            Creates a scatter plot that is colormapped according to 
            score values.

        peak_id - None or int
        (optional, but required to plot peak characteristic and shift overlays)
            If int, the peak id for plotting characteristics of.
            To identify peak id's, use the plot_peak_ids function, which will
            overlay the average image with the identified peaks used
            throughout the image series.

        plot_char - None or int
        (optional, but required to plot peak characteristic overlays)
            If int, the id of the characteristic to plot as the colored 
            scatter plot.
            Possible components are:
               4: peak height
               5: peak orientation
               6: peak eccentricity

        plot_shifts - bool, optional
            If True, plots shift overlays for given peak_id onto the parent image(s)

        """
        smp=self.mapped_parameters
        if not hasattr(smp, "original_files"):
            messages.warning("""No original files available.  Can't map anything to nothing.
If you use the cell_cropper function to crop your cells, the cell locations and original files 
will be tracked for you.""")
            return None
        if peak_id is not None and (plot_shifts is False and plot_char is None):
            messages.warning("""Peak ID provided, but no plot_char given , and plot_shift disabled.
Nothing to plot.  Try again.""")
            return None

        keys=smp.original_files.keys()

        nfigs=len(keys)
        if nfigs<per_row: per_row=nfigs

        flist=[]

        if same_window:
            rows=int(np.ceil(nfigs/float(per_row)))
            f=plt.figure(figsize=(4*per_row,3*rows))
        for i in xrange(len(keys)):
            if same_window:
                ax=f.add_subplot(rows,per_row,i+1)
            else:
                f=plt.figure()
                ax=plt.add_subplot(111)
            locs=smp.locations.copy()
            mask=locs['filename']==keys[i]
            mask=mask.squeeze()
            # grab the array of peak locations, only from THIS image
            locs=locs[mask]['position'].squeeze()
            image=smp.original_files[keys[i]].data
            axes_manager=smp.original_files[keys[i]].axes_manager
            cbar_label=None
            if peak_id<>None:
                # add the offset for the desired peak so that it lies on top of the peak in the image.
                pk_loc=smp.peak_chars[:,mask][7*peak_id:7*peak_id+2].T
                locs=locs+pk_loc
            if plot_char<>None:
                char=self._get_pk_char(f_pc[:,mask], locations=locs, plot_char=plot_char, peak_id=peak_id)
                id_label=peak_id
                if plot_char==4:
                    cbar_label='Peak Height'
                elif plot_char==5:
                    cbar_label='Peak Orientation'
                elif plot_char==6:
                    cbar_label='Peak Eccentricity'
            elif plot_component<>None:
                char=self._get_pk_char(f_pc[:,mask], locations=locs, plot_char=plot_char, comp_id=plot_component)
                id_label=plot_component
                cbar_label='Score'
            else: char=None
            if plot_shifts:
                shifts=self._get_pk_shifts(f_pc[:,mask], locations=locs)
            else: shifts=None
            if comp_label:
                label=comp_label+'%i:\n%s'%(id_label,keys[i])
            else:
                label=keys[i]
            ax=sigdraw._plot_quiver_scatter_overlay(image=image, axes_manager=axes_manager,
                                                 calibrate=calibrate, shifts=shifts,
                                                 char=char, comp_label=label,
                                                 img_cmap=img_cmap, sc_cmap=sc_cmap,
                                                 quiver_color=quiver_color,ax=ax,
                                                 vector_scale=vector_scale,
                                                 cbar_label=cbar_label)
            if not same_window:
                flist.append(f)
        try:
            plt.tight_layout()
        except:
            pass
        if same_window:
            flist.append(f)
        return flist

    def plot_peak_overlay_cell(self, img_ids=None, calibrate=True,
                        same_window=True, comp_label='img', 
                        plot_shifts=True, plot_char=None, quiver_color='white',
                        vector_scale=1,
                        cmap=plt.cm.jet, per_row=3):
        """Overlays peak characteristics on an image plot of the average image.

        Parameters
        ----------

        img_ids : None, int, or list of ints
            if None, returns maps of average image.
            if int, returns maps of characteristics with ids from 0 to given int.
            if list of ints, returns maps of characteristics with ids in given list.

        calibrate : bool
            if True, calibrates plots where calibration is available from
            the axes_manager.  If False, plots are in pixels/channels.

        same_window : bool
            if True, plots each factor to the same window.  They are not scaled.
        
        comp_label : string, the label that is either the plot title (if plotting in
            separate windows) or the label in the legend (if plotting in the 
            same window)

        cmap : The colormap used for the factor image, or for peak 
            characteristics, the colormap used for the scatter plot of
            some peak characteristic.
        
        per_row : int, the number of plots in each row, when the same_window
            parameter is True.

        plot_char - None or int
        (optional, but required to plot peak characteristic overlays)
            If int, the id of the characteristic to plot as the colored 
            scatter plot.
            Possible components are:
               0 or 1: peak coordinates
               2 or 3: position difference relative to nearest target location
               4: peak height
               5: peak orientation
               6: peak eccentricity

        plot_shift - bool, optional
            If True, plots shift overlays from the factor onto the image given in
            the cell_data parameter
        """
        smp=self.mapped_parameters
        factors=smp.peak_chars
        #slice the images based on the img_ids
        if img_ids is not None:
            if not hasattr(img_ids,'__iter__'):
                img_ids=range(img_ids)
            mask=np.zeros(self.data.shape[0],dtype=np.bool)
            for idx in img_ids:
                mask[idx]=1
            img_data=self.data[mask]
            avg_char=False
        else:
            img_data=None
            avg_char=True
        return self._plot_factors_or_pchars(factors=factors, comp_ids=img_ids,
                                     calibrate=calibrate, comp_label=comp_label,
                                     img_data=img_data,avg_char=avg_char,
                                     on_peaks=True, plot_char=plot_char,
                                     plot_shifts=plot_shifts, cmap=cmap,
                                     quiver_color=quiver_color,
                                     vector_scale=vector_scale,
                                     per_row=per_row)

    def plot_peak_overlay_image(self, peak_ids=None, calibrate=True,
                                plot_shifts=False, plot_char=None,
                                same_window=True, comp_label=None, 
                                cmap=plt.cm.jet, no_nans=True, per_row=3,
                                quiver_color='white',vector_scale=1):

        """Overlays peak characteristics on an image plot.
        
        Analogous to score plots, except that this allows you to examine how one
        particular peak is varying across an image.

        Parameters
        ----------
        peak_ids : int or list of ints
            if int, returns maps of peaks with ids from 0 to given int.
            if list of ints, returns maps of peaks with ids in given list.

        calibrate : bool
            if True, calibrates plots where calibration is available from
            the axes_manager.  If False, plots are in pixels/channels.

        same_window : bool
            if True, plots each factor to the same window.  They are not scaled.
        
        comp_label : string, the label that is either the plot title (if plotting in
            separate windows) or the label in the legend (if plotting in the 
            same window)

        cmap : The colormap used for the factor image, or for peak 
            characteristics, the colormap used for the scatter plot of
            some peak characteristic.
        
        per_row : int, the number of plots in each row, when the same_window
            parameter is True.

        plot_char - None or int
        (optional, but required to plot peak characteristic overlays)
            If int, the id of the characteristic to plot as the colored 
            scatter plot.
            Possible components are:
               0 or 1: peak coordinates
               2 or 3: position difference relative to nearest target location
               4: peak height
               5: peak orientation
               6: peak eccentricity

        plot_shift - bool, optional
            If True, plots shift overlays from the factor onto the image given in
            the cell_data parameter
        """
        peak_chars=self.mapped_parameters.peak_chars
        
        return self._plot_scores_or_peak_char(peak_chars,
                                 calibrate=calibrate,
                                 same_window=same_window, comp_label=comp_label,cmap=cmap,
                                 no_nans=no_nans,per_row=per_row,
                                 peak_ids=peak_ids,plot_char=plot_char,
                                 plot_shifts=plot_shifts,
                                 quiver_color=quiver_color,
                                 vector_scale=vector_scale)

    def plot_ica_peak_factors(self, comp_ids=None, calibrate=True,
                        same_window=True, comp_label='IC', 
                        img_data=None,
                        plot_shifts=True, plot_char=None, 
                        cmap=plt.cm.jet, per_row=3):
        """Overlays peak characteristics on an image plot of the average image.

        Parameters
        ----------

        comp_ids : None, int, or list of ints
            if None, returns maps of all components.
            if int, returns maps of components with ids from 0 to given int.
            if list of ints, returns maps of components with ids in given list.

        calibrate : bool
            if True, calibrates plots where calibration is available from
            the axes_manager.  If False, plots are in pixels/channels.

        same_window : bool
            if True, plots each factor to the same window.  They are not scaled.
        
        comp_label : string, the label that is either the plot title (if plotting in
            separate windows) or the label in the legend (if plotting in the 
            same window)

        on_peaks : bool
            Plot peak characteristics (True), or factor images (False)

        cmap : The colormap used for the factor image, or for peak 
            characteristics, the colormap used for the scatter plot of
            some peak characteristic.
        
        per_row : int, the number of plots in each row, when the same_window
            parameter is True.

        img_data : 2D numpy array
            This is the image that gets overlaid with the peak information. If 
            not specified, defaults to the average image of your image stack.

        plot_char - None or int
        (optional, but required to plot peak characteristic overlays)
            If int, the id of the characteristic to plot as the colored 
            scatter plot.
            Possible components are:
               0 or 1: peak coordinates
               2 or 3: position difference relative to nearest target location
               4: peak height
               5: peak orientation
               6: peak eccentricity

        plot_shifts - bool, optional
            If True, plots shift overlays from the factor onto the image given in
            the cell_data parameter
        """
        factors=self.peak_mva_results.ic
        return self._plot_factors_or_pchars(factors=factors, comp_ids=comp_ids,
                                     calibrate=calibrate, comp_label=comp_label,
                                     img_data=img_data,
                                     on_peaks=True, plot_char=plot_char,
                                     plot_shifts=plot_shifts, cmap=cmap,
                                     quiver_color=quiver_color,
                                     vector_scale=vector_scale,
                                     per_row=per_row)

    def plot_pca_peak_factors(self, comp_ids=6, calibrate=True,
                        same_window=True, comp_label='PC', 
                        img_data=None,
                        plot_shifts=True, plot_char=None, 
                        quiver_color='white',vector_scale=1,
                        cmap=plt.cm.jet, per_row=3):
        """Overlays PCA-derived peak characteristics on an image plot.

        Parameters
        ----------

        comp_ids : None, int, or list of ints
            if None, returns maps of all components.
            if int, returns maps of components with ids from 0 to given int.
            if list of ints, returns maps of components with ids in given list.

        calibrate : bool
            if True, calibrates plots where calibration is available from
            the axes_manager.  If False, plots are in pixels/channels.

        same_window : bool
            if True, plots each factor to the same window.  They are not scaled.
        
        comp_label : string, the label that is either the plot title (if plotting in
            separate windows) or the label in the legend (if plotting in the 
            same window)

        on_peaks : bool
            Plot peak characteristics (True), or factor images (False)

        cmap : The colormap used for the factor image, or for peak 
            characteristics, the colormap used for the scatter plot of
            some peak characteristic.
        
        per_row : int, the number of plots in each row, when the same_window
            parameter is True.

        img_data : 2D numpy array
            This is the image that gets overlaid with the peak information. If 
            not specified, defaults to the average image of your image stack.

        plot_char - None or int
        (optional, but required to plot peak characteristic overlays)
            If int, the id of the characteristic to plot as the colored 
            scatter plot.
            Possible components are:
               0 or 1: peak coordinates
               2 or 3: position difference relative to nearest target location
               4: peak height
               5: peak orientation
               6: peak eccentricity

        plot_shifts - bool, optional
            If True, plots shift overlays from the factor onto the image given in
            the cell_data parameter
        """
        factors=self.peak_mva_results.pc
        return self._plot_factors_or_pchars(factors=factors, comp_ids=comp_ids,
                                     calibrate=calibrate, comp_label=comp_label,
                                     img_data=img_data,
                                     on_peaks=True, plot_char=plot_char,
                                     plot_shifts=plot_shifts, cmap=cmap,
                                     quiver_color=quiver_color,
                                     vector_scale=vector_scale,
                                     per_row=per_row)

    def plot_ica_peak_factors(self, comp_ids=None, calibrate=True,
                        same_window=True, comp_label='IC', 
                        img_data=None,
                        plot_shifts=True, plot_char=None, 
                        quiver_color='white',vector_scale=1,
                        cmap=plt.cm.jet, per_row=3):
        """Overlays ICA-derived peak characteristics on an image plot.

        Parameters
        ----------

        comp_ids : None, int, or list of ints
            if None, returns maps of all components.
            if int, returns maps of components with ids from 0 to given int.
            if list of ints, returns maps of components with ids in given list.

        calibrate : bool
            if True, calibrates plots where calibration is available from
            the axes_manager.  If False, plots are in pixels/channels.

        same_window : bool
            if True, plots each factor to the same window.  They are not scaled.
        
        comp_label : string, the label that is either the plot title (if plotting in
            separate windows) or the label in the legend (if plotting in the 
            same window)

        on_peaks : bool
            Plot peak characteristics (True), or factor images (False)

        cmap : The colormap used for the factor image, or for peak 
            characteristics, the colormap used for the scatter plot of
            some peak characteristic.
        
        per_row : int, the number of plots in each row, when the same_window
            parameter is True.

        img_data : 2D numpy array
            This is the image that gets overlaid with the peak information. If 
            not specified, defaults to the average image of your image stack.

        plot_char - None or int
        (optional, but required to plot peak characteristic overlays)
            If int, the id of the characteristic to plot as the colored 
            scatter plot.
            Possible components are:
               0 or 1: peak coordinates
               2 or 3: position difference relative to nearest target location
               4: peak height
               5: peak orientation
               6: peak eccentricity

        plot_shifts - bool, optional
            If True, plots shift overlays from the factor onto the image given in
            the cell_data parameter
        """
        factors=self.peak_mva_results.ic
        return self._plot_factors_or_pchars(factors=factors, comp_ids=comp_ids,
                                     calibrate=calibrate, comp_label=comp_label,
                                     img_data=img_data,
                                     on_peaks=True, plot_char=plot_char,
                                     plot_shifts=plot_shifts, cmap=cmap,
                                     quiver_color=quiver_color,
                                     vector_scale=vector_scale,
                                     per_row=per_row)

    def kmeans_cluster_stack(self, cells, clusters=None):
        import mdp
        if self._unfolded:
            self.fold()
        # if clusters not given, try to determine what it should be.
        if clusters is None:
            pass
        d=cells
        kmeans=mdp.nodes.KMeansClassifier(clusters)
        cluster_arrays=[]
    
        avg_stack=np.zeros((clusters,d.shape[1],d.shape[2]))
        kmeans.train(d.reshape((-1,d.shape[0])).T)
        kmeans.stop_training()
        groups=kmeans.label(d.reshape((-1,d.shape[0])).T)
        try:
            # test if location data is available
            self.mapped_parameters.locations[0]
        except:
            messages.warning("No cell location information was available.")
        for i in xrange(clusters):
            # get number of members of this cluster
            members=groups.count(i)
            cluster_array=np.zeros((members,d.shape[1],d.shape[2]))
            cluster_idx=0
            positions=np.zeros((members,3))
            for j in xrange(len(groups)):
                if groups[j]==i:
                    cluster_array[cluster_idx,:,:]=d[j,:,:]
                    try:
                        positions[cluster_idx]=self.mapped_parameters.locations[j]
                    except:
                        pass
                    cluster_idx+=1
            cluster_array_Image=Image({
                'data':avg_stack,
                'mapped_parameters':{
                    'title' : 'Cluster %s from %s'%(i,
                        self.mapped_parameters.title),
                    'locations':positions,
                    'members':members,}
            })
            cluster_arrays.append(cluster_array_Image)
            avg_stack[i,:,:]=np.sum(cluster_array,axis=0)
        members_list=[groups.count(i) for i in xrange(clusters)]
        avg_stack_Image=Image({'data':avg_stack,
                    'mapped_parameters':{
                        'title':'Cluster averages from %s'%self.mapped_parameters.title,
                        'member_counts':members_list,
                        }
                    })
        return avg_stack_Image, cluster_arrays

    def _plot_quiver_scatter_overlay(self, image, calibrate=True, shifts=None, 
                                     char=None, ax=None, comp_label=None,
                                     img_cmap=plt.cm.gray,
                                     sc_cmap=plt.cm.jet,
                                     quiver_color='white',
                                     vector_scale=1,
                                     cbar_label=None
                                     ):
        """quiver plot notes:
           
           The vector_scale parameter scales the quiver
               plot arrows.  The vector is defined as
               one data unit along the X axis.  If shifts
               are small, set vector_scale so that when
               they are multiplied by vector_scale, they
               are on the scale of the image plot.
        """
        if ax==None:
            ax=plt.gca()
        extent=None
        if shifts is not None:
            slocs=shifts['location'].squeeze().copy()
            shifts=shifts['shift'].squeeze().copy()
        if char is not None:
            clocs=char['location'].squeeze().copy()        
        """
        if calibrate:
            extent=(axes[1].low_value,
                    axes[1].high_value,
                    axes[0].high_value,
                    axes[0].low_value)
            if shifts is not None:                
                slocs[:,0]=slocs[:,0]*axes[0].scale+axes[0].offset
                slocs[:,1]=slocs[:,1]*axes[1].scale+axes[1].offset
                shifts[:,0]=shifts[:,0]*axes[0].scale+axes[0].offset
                shifts[:,1]=shifts[:,1]*axes[1].scale+axes[1].offset
            if char is not None:
                clocs[:,0]=clocs[:,0]*axes[0].scale+axes[0].offset
                clocs[:,1]=clocs[:,1]*axes[1].scale+axes[1].offset
        """
        ax.imshow(image,interpolation='nearest',
                  cmap=img_cmap,extent=extent)
        if comp_label:
            plt.title(comp_label)
        if shifts is not None:
            ax.quiver(slocs[:,0],slocs[:,1],
                      shifts[:,0], shifts[:,1],
                      units='x',color=quiver_color,
                      scale=vector_scale, scale_units='x')
        if char is not None:
            sc=ax.scatter(clocs[:,0],clocs[:,1],
                       c=char['char'], cmap=sc_cmap)
            div=make_axes_locatable(ax)
            cax=div.append_axes('right',size="5%",pad=0.05)
            cb=plt.colorbar(sc,cax=cax)
            if cbar_label:
                cb.set_label(cbar_label)
        if extent:
            ax.set_xlim(extent[:2])
            ax.set_ylim(extent[2:])
        else:
            ax.set_xlim(0,image.shape[0])
            ax.set_ylim(image.shape[1],0)
        return ax
    
    def plot_image_peaks(img_data, locations, plot_ids=False, ax=None):
        if ax is None:
            ax=plt.gca()
        ax.imshow(img_data,cmap=plt.gray(), 
                interpolation = 'nearest')
        if plot_ids:
            for pk_id in xrange(locations.shape[0]):
                plt.text(locations[pk_id,0], locations[pk_id,1], 
                         "%s"%pk_id, size=10, rotation=0.,
                         ha="center", va="center",
                         bbox = dict(boxstyle="round",
                                     ec=(1., 0.5, 0.5),
                                     fc=(1., 0.8, 0.8),
                                     )
                         )
        else:
            ax.scatter(locations[:,0],locations[:,1])
            ax.set_xlim(0,img_data.shape[0]-1)
            ax.set_ylim(img_data.shape[1]-1,0)
        return ax