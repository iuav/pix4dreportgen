import untangle
import pandas as pd

obj1 = untangle.parse("/PATH/TO/THE/report1.xml")
obj2 = untangle.parse("/PATH/TO/THE/report2.xml")
obj3 = untangle.parse("/PATH/TO/THE/report3.xml")
xmls = [obj1, obj2, obj3]

tempsumdf = pd.DataFrame()
temp3d2ddf = pd.DataFrame()
temp2ddf = pd.DataFrame()
tempgcp1df = pd.DataFrame()
tempgcp2df = pd.DataFrame()


def tablesummary(obj, n):

    sumtablecol1 = ['Summary', '', '', '', '', 'Quality check', '', '', '', 'Bundle Block Adjustment Details', '', '', '',
                    'Internal Camera Parameters', '', '', '', '', '', '', '', '']
    sumtablecol2 = ['Project', 'Processed date', 'Camera Model Name(s)', 'Average Ground Sampling Distance (GSD)', '',
                    'No. of Images', 'No. of calibrated images', 'Percentage relative diff in camera parameters', '',
                    'Number of 2D Keypoint Observations for Bundle Block Adjustment',
                    'Number of 3D Points for Bundle Block Adjustment', 'Mean Reprojection Error [pixels]', '',
                    'Initial Focal Length', 'Optimised Focal Length', 'Focal length Uncertainties',
                    'Initial Principal Point (x)', 'Optimised Principal Point (x)', 'Principal point (x) Uncertainties',
                    'Initial Principal Point (y)', 'Optimised Principal Point (y)', 'Principal point (y) Uncertainties']
    sumtablecol3 = ['Initial', 'After GCP', 'Final']

    global tempsumdf

    # 1-Summary
    projectname = obj.report['project']
    processeddate = obj.report['processed']
    avggsd=(obj.report.results.initial.gsd['cm'] + " cm / " + obj.report.results.initial.gsd['inches'] + " in")
    cameraname = obj.report.results.initial.camera['name']

    # 2-Quality check
    noimages = obj.report.results.initial.images['total']
    nocalibimages = obj.report.results.initial.images['calibrated']
    percentdiffcam = obj.report.results.initial.cameraOptimization['relativeDifference']

    # 3-Bundle Block
    no2dkeypts = obj.report.results.initial.trackHistogram['observed2DPoints']
    no3dkeypts = obj.report.results.initial.trackHistogram['numberOf3DPoints']
    meanreprojerror = obj.report.results.initial.atps['meanProjectionError']

    # 4-Internal Camera Parameters
    initfocallength = (obj.report.results.initial.camera.initialValues.focalLengthmm.cdata + " mm")
    optimfocallength = (obj.report.results.initial.camera.optimizedValues.focalLengthmm.cdata + " mm")
    uncertainfocallength = (obj.report.results.initial.camera.uncertainties.focalLengthmm.cdata + " mm")

    initprincptx = (obj.report.results.initial.camera.initialValues.principalPointXPixel.cdata + " pixel " + obj.report.results.initial.camera.initialValues.principalPointXmm.cdata + " mm")
    optimprincptx = (obj.report.results.initial.camera.optimizedValues.principalPointXPixel.cdata + " pixel " + obj.report.results.initial.camera.optimizedValues.principalPointXmm.cdata + " mm")
    uncertainprincptx=(obj.report.results.initial.camera.uncertainties.principalPointXPixel.cdata + " pixel ")

    initprincpty = (obj.report.results.initial.camera.initialValues.principalPointYPixel.cdata + " pixel " + obj.report.results.initial.camera.initialValues.principalPointYmm.cdata + " mm")
    optimprincpty = (obj.report.results.initial.camera.optimizedValues.principalPointYPixel.cdata + " pixel " + obj.report.results.initial.camera.optimizedValues.principalPointYmm.cdata + " mm")
    uncertainprincpty = (obj.report.results.initial.camera.uncertainties.principalPointYPixel.cdata + " pixel ")

    # 1,2,3,4 Combined Report
    sumtabledatacol = [projectname, processeddate, cameraname, avggsd, '', noimages, nocalibimages, percentdiffcam, '', no2dkeypts, no3dkeypts, meanreprojerror, '', initfocallength, optimfocallength, uncertainfocallength, initprincptx, optimprincptx, uncertainprincptx, initprincpty, optimprincpty, uncertainprincpty]
    if n == 0:
        sumtabledf = pd.DataFrame({'': sumtablecol1, 'Parameter': sumtablecol2, sumtablecol3[n]: sumtabledatacol})
    else:
        sumtabledf = pd.DataFrame({sumtablecol3[n]: sumtabledatacol})
    finalpd = pd.concat([tempsumdf, sumtabledf], axis=1)
    finalpd.to_csv('sumtable.csv', index=False, encoding='utf-8')
    tempsumdf = finalpd


def table3dto2dkeys(obj):

    global temp3d2ddf

    # 5-3D Points from 2D Keypoints Matches Table
    tracklist = obj.report.results.initial.trackHistogram.get_elements()
    imagelist = []
    pointslist = []
    for track in tracklist:
        imagelist.append(track['images'])
        pointslist.append(track['points3D'])

    df3dto2d = pd.DataFrame({'Images observed': imagelist, '3D Points observed': pointslist})
    finaldf3dto2d = pd.concat([temp3d2ddf, df3dto2d], axis=1)
    finaldf3dto2d.to_csv('3dto2d.csv', index=False, encoding='utf-8')
    temp3d2ddf = finaldf3dto2d


def table2dkeys(obj, n):

    global temp2ddf

    # 6-2D Keypoints Table
    points2Dkeylist = obj.report.results.initial.points2D.general.keypoints.get_elements()
    keylist2d = []
    for point in points2Dkeylist:
        median2d = point['median']
        max2d = point['max']
        min2d = point['min']
        mean2d = point['mean']
        keylist2d.extend((median2d,min2d,max2d,mean2d))

    points2Dtracklist = obj.report.results.initial.points2D.general.tracks.get_elements()
    tracklist2d = []
    for point in points2Dtracklist:
        median2d = point['median']
        max2d = point['max']
        min2d = point['min']
        mean2d = point['mean']
        tracklist2d.extend((median2d,min2d,max2d,mean2d))

    typecol = ['Median', 'Min', 'Max', 'Mean']
    if n == 0:
        df2dkey = pd.DataFrame({'': typecol, 'Number of 2D Keypoints per Image': keylist2d, 'Number of Matched 2D Keypoints per Image': tracklist2d})
    else:
        df2dkey = pd.DataFrame({'Number of 2D Keypoints per Image': keylist2d, 'Number of Matched 2D Keypoints per Image': tracklist2d})
    final2d = pd.concat([temp2ddf, df2dkey], axis=1)
    final2d.to_csv('2dkeytable.csv', index=False, encoding='utf-8')
    temp2ddf = final2d


def tablegeoloc(obj, n):

    global tempgcp1df
    global tempgcp2df

    # 7-Geolocation Details-GCP

    if n == 0:
        gcpinit = pd.DataFrame({'NO': [], 'GCP': [], 'Data': [], "For Initial Step": []})
        finalgcpinit1 = pd.concat([tempgcp1df, gcpinit], axis=1)
        finalgcpinit1.to_csv('gcpgeo.csv', index=False, encoding='utf-8')
        finalgcpinit2 = pd.concat([tempgcp2df, gcpinit], axis=1)
        finalgcpinit2.to_csv('gcpgeo.csv', mode='a', index=False, encoding='utf-8')
        tempgcp1df = finalgcpinit2
        tempgcp2df = finalgcpinit2

    else:

        gcpname = []
        verified = []
        x = []
        y = []
        z = []
        pixel = []
        gcplist = obj.report.results.initial.statsControlPoints.gcps.inliers.get_elements()
        for gcp in gcplist:
            gcpname.append(gcp['name'])
            verified.append((gcp['inliers'], gcp['valid']))
            x.append(gcp.error['x'])
            y.append(gcp.error['y'])
            z.append(gcp.error['z'])
            pixel.append(gcp.error['pixel'])

        gcpname.extend(('Mean[m]', 'Sigma[m]', 'RMS Error[m]', 'Inaccurate Checkpoints below',))
        gcpavg = obj.report.results.initial.statsControlPoints.gcps.avg
        x.append(gcpavg['x'])
        y.append(gcpavg['y'])
        z.append(gcpavg['z'])
        pixel.append('')
        verified.append('')

        gcpsigma = obj.report.results.initial.statsControlPoints.gcps.stdev
        x.append(gcpsigma['x'])
        y.append(gcpsigma['y'])
        z.append(gcpsigma['z'])
        pixel.append('')
        verified.append('')

        gcprms = obj.report.results.initial.statsControlPoints.gcps.rms
        x.append(gcprms['x'])
        y.append(gcprms['y'])
        z.append(gcprms['z'])
        pixel.append('')
        verified.append('')

        x.append(''), y.append(''), z.append(''), pixel.append(''), verified.append('')

        gcptable1 = pd.DataFrame({'GCP Name': gcpname, 'Error X[m]': x, 'Error Y[m]': y, 'Error Z[m]': z, 'Projection Error [pixel]': pixel, 'Verified/Marked': verified})
        finalgcp1 = pd.concat([tempgcp1df, gcptable1], axis=1)
        finalgcp1.to_csv('gcpgeo.csv', index=False, encoding='utf-8')
        tempgcp1df = finalgcp1

        # 7.1-Inaccurate GCPs
        inaccgcplist = obj.report.results.initial.statsControlPoints.checkPoints.inliers.get_elements()
        inaccgcpname = []
        inaccverified = []
        inaccx = []
        inaccy = []
        inaccz = []
        inaccpixel = []
        for gcp in inaccgcplist:
            inaccgcpname.append(gcp['name'])
            inaccverified.append((gcp['inliers'], gcp['valid']))
            inaccx.append(gcp.error['x'])
            inaccy.append(gcp.error['y'])
            inaccz.append(gcp.error['z'])
            inaccpixel.append(gcp.error['pixel'])

        inaccgcpname.extend(('Mean[m]', 'Sigma[m]', 'RMS Error[m]'))

        gcpavg = obj.report.results.initial.statsControlPoints.checkPoints.avg
        inaccx.append(gcpavg['x'])
        inaccy.append(gcpavg['y'])
        inaccz.append(gcpavg['z'])
        inaccpixel.append('')
        inaccverified.append('')

        gcpsigma = obj.report.results.initial.statsControlPoints.checkPoints.stdev
        inaccx.append(gcpsigma['x'])
        inaccy.append(gcpsigma['y'])
        inaccz.append(gcpsigma['z'])
        inaccpixel.append('')
        inaccverified.append('')

        gcprms = obj.report.results.initial.statsControlPoints.checkPoints.rms
        inaccx.append(gcprms['x'])
        inaccy.append(gcprms['y'])
        inaccz.append(gcprms['z'])
        inaccpixel.append('')
        inaccverified.append('')

        gcptable2 = pd.DataFrame({'Check Point Name': inaccgcpname, 'Error X[m]': inaccx, 'Error Y[m]': inaccy, 'Error Z[m]': inaccz, 'Projection Error [pixel]': inaccpixel, 'Verified/Marked': inaccverified})
        finalgcp2 = pd.concat([tempgcp2df, gcptable2], axis=1)
        finalgcp2.to_csv('gcpgeo.csv', mode='a', index=False, encoding='utf-8')
        tempgcp2df = finalgcp2


def main():

    for n in range(len(xmls)):
        tablesummary(xmls[n], n)
        table3dto2dkeys(xmls[n])
        table2dkeys(xmls[n], n)
        tablegeoloc(xmls[n], n)

if __name__ == '__main__':
    main()