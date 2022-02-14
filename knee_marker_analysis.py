import json
from zlib import Z_PARTIAL_FLUSH
import xlsxwriter
import numpy as np
import math


def knee_marker_analyse_file(data_path):
    # Load data from JSON
    with open(data_path) as json_file:
        data = json.load(json_file)

    return knee_marker_analysis(data)


def knee_marker_analysis(data):
    # Clean up data
    marker = {x['name']: np.asarray(x['pos'][:3]) for x in data['markers']}

    # --- Insall Salvati Ratio (IS) ---
    i_s_R, i_s_L = None, None
    try:
        i_s_R = insall_salvati(marker['Sup_Pat_R'], marker['Inf_Pat_R'],
                               marker['Tub_Tib_R'])
    except KeyError as exception:
        print(f'Error: Markers missing; Will continue without Insall Salvati R calculation: {exception}')

    try:
        i_s_L = insall_salvati(marker['Sup_Pat_L'], marker['Inf_Pat_L'],
                               marker['Tub_Tib_L'])
    except KeyError as exception:
        print(f'Error: Markers missing; Will continue without Insall Salvati L calculation: {exception}')

    # --- Lateral Translation (LT) ---
    lt_R, lt_L = None, None
    try:
        lt_R = lateral_translation(marker['Ant_Pat_R'], marker['Pos_Pat_R'], 
                                   marker['Sulc_R'])
    except KeyError as exception:
        print(f'Error: Markers missing; Will continue without Lateral Translation R calculation: {exception}')

    try:
        lt_L = lateral_translation(marker['Ant_Pat_L'], marker['Pos_Pat_L'],
                                   marker['Sulc_L'])
    except KeyError as exception:
        print(f'Error: Markers missing; Will continue without Lateral Translation L calculation: {exception}')

    # --- TT-TG Distance (tttg) ---
    tttg_R, tttg_L = None, None
    try:
        tttg_R = tt_tg(marker['Med_Pos_Cond_R'], marker['Lat_Pos_Cond_R'],
                       marker['Tub_Tib_R'], marker['Sulc_R'])
    except KeyError as exception:
        print(f'Error: Markers missing; Will continue without TT-TG R calculation: {exception}')

    try:
        tttg_L = tt_tg(marker['Med_Pos_Cond_L'], marker['Lat_Pos_Cond_L'],
                       marker['Tub_Tib_L'], marker['Sulc_L'])
    except KeyError as exception:
        print(f'Error: Markers missing; Will continue without TT-TG L calculation: {exception}')

    # --- Patellar Tilt (pt) ---
    pt_R, pt_L = None, None
    try:
        pt_R = pat_tilt(marker['Med_Pat_R'], marker['Lat_Pat_R'], marker['Med_Pos_Cond_R'],
                        marker['Lat_Pos_Cond_R'])
    except KeyError as exception:
        print(f'Error: Markers missing; Will continue without Patellar Tilt R calculation: {exception}')

    try:
        pt_L = pat_tilt(marker['Med_Pat_L'], marker['Lat_Pat_L'], marker['Med_Pos_Cond_L'],
                        marker['Lat_Pos_Cond_L'])
    except KeyError as exception:
        print(f'Error: Markers missing; Will continue without Patellar Tilt L calculation: {exception}')

    # --- Lateral Patellar Tilt (lpt) ---
    lpt_R, lpt_L = None, None
    try:
        lpt_R = lat_pat_tilt(marker['Pos_Pat_R'], marker['Lat_Pat_R'],
                             marker['Med_Ant_Cond_R'], marker['Lat_Ant_Cond_R'])
    except KeyError as exception:
        print(f'Error: Markers missing; Will continue without Lateral Patellar Tilt R calculation: {exception}')

    try:
        lpt_L = lat_pat_tilt(marker['Pos_Pat_L'], marker['Lat_Pat_L'],
                             marker['Med_Ant_Cond_L'], marker['Lat_Ant_Cond_L'])
    except KeyError as exception:
        print(f'Error: Markers missing; Will continue without Lateral Patellar Tilt L calculation: {exception}')

    # --- Bisect Offset (bo) ---
    bo_R, bo_L = None, None
    try:
        bo_R = bis_offset(marker['Sulc_R'], marker['Med_Pos_Cond_R'],
                          marker['Lat_Pos_Cond_R'], marker['Lat_Pat_R'],
                          marker['Med_Pat_R'])
    except KeyError as exception:
        print(f'Error: Markers missing; Will continue without Bisect Offset R calculation: {exception}')

    try:
        bo_L = bis_offset(marker['Sulc_L'], marker['Med_Pos_Cond_L'],
                          marker['Lat_Pos_Cond_L'], marker['Lat_Pat_L'],
                          marker['Med_Pat_L'])
    except KeyError as exception:
        print(f'Error: Markers missing; Will continue without Bisect Offset L calculation: {exception}')

    # --- Sulcus Angle (sa) ---
    sa_R, sa_L = None, None
    try:
        sa_R = sulc_angle(marker['Lat_Ant_Cond_R'], marker['Med_Ant_Cond_R'],
                          marker['Sulc_R'])
    except KeyError as exception:
        print(f'Error: Markers missing; Will continue without Sulcus Angle R calculation: {exception}')

    try:
        sa_L = sulc_angle(marker['Lat_Ant_Cond_L'], marker['Med_Ant_Cond_L'],
                          marker['Sulc_L'])
    except KeyError as exception:
        print(f'Error: Markers missing; Will continue without Sulcus Angle L calculation: {exception}')

    # --- Inclination (incl) ---
    lat_incl_R, med_incl_R, lat_incl_L, med_incl_L = None, None, None, None
    try:
        lat_incl_R, med_incl_R = inclination(marker['Lat_Ant_Cond_R'], marker['Med_Ant_Cond_R'],
                                             marker['Sulc_R'], marker['Med_Pos_Cond_R'],
                                             marker['Lat_Pos_Cond_R'])
    except KeyError as exception:
        print(f'Error: Markers missing; Will continue without Inclination R calculation: {exception}')

    try:
        lat_incl_L, med_incl_L = inclination(marker['Lat_Ant_Cond_L'], marker['Med_Ant_Cond_L'],
                                             marker['Sulc_L'], marker['Med_Pos_Cond_L'],
                                             marker['Lat_Pos_Cond_L'])
    except KeyError as exception:
        print(f'Error: Markers missing; Will continue without Inclination L calculation: {exception}')

    # --- Trochlear Depth (td) ---
    td_R, td_L = None, None
    try:
        td_R = depth_troch(marker['Med_Ant_Cond_R'], marker['Lat_Ant_Cond_R'],
                           marker['Sulc_R'])
    except KeyError as exception:
        print(f'Error: Markers missing; Will continue without Trochlear Depth R calculation: {exception}')

    try:
        td_L = depth_troch(marker['Med_Ant_Cond_L'], marker['Lat_Ant_Cond_L'],
                           marker['Sulc_L'])
    except KeyError as exception:
        print(f'Error: Markers missing; Will continue without Trochlear Depth L calculation: {exception}')

    # --- Modified Insall-Salvati (mis), Caton-Deschamps (cd), Blackburne-Peele (bp)  ---
    mis_R, cd_R, bp_R, mis_L, cd_L, bp_L = None, None, None, None, None, None
    try:
        mis_R, cd_R, bp_R = cd_bp_mis(marker['Sup_Pat_R'], marker['Inf_Art_Pat_R'],
                                      marker['Sup_Ant_Tib_R'], marker['Tub_Tib_R'],
                                      marker['Sup_Tib_R'])
    except KeyError as exception:
        print(f'Error: Markers missing; Will continue without Ratio R calculation: {exception}')

    try:
        mis_L, cd_L, bp_L = cd_bp_mis(marker['Sup_Pat_L'], marker['Inf_Art_Pat_L'],
                                      marker['Sup_Ant_Tib_L'], marker['Tub_Tib_L'],
                                      marker['Sup_Tib_L'])
    except KeyError as exception:
        print(f'Error: Markers missing; Will continue without Ratio L calculation: {exception}')

    # --- Trochlear Angle (TA) ---
    ta_R, ta_L = None, None
    try:
        ta_R = troch_angle(marker['Med_Ant_Cond_R'], marker['Lat_Ant_Cond_R'],
                           marker['Med_Pos_Cond_R'], marker['Lat_Pos_Cond_R'])
    except KeyError as exception:
        print(f'Error: Markers missing; Will continue without Trochlear Angle R calculation: {exception}')

    try:
        ta_L = troch_angle(marker['Med_Ant_Cond_L'], marker['Lat_Ant_Cond_L'],
                           marker['Med_Pos_Cond_L'], marker['Lat_Pos_Cond_L'])
    except KeyError as exception:
        print(f'Error: Markers missing; Will continue without Trochlear Angle L calculation: {exception}')

    # Output data
    return(i_s_R, lt_R, tttg_R, pt_R, lpt_R, bo_R, sa_R, lat_incl_R, med_incl_R, td_R, mis_R, cd_R, bp_R, ta_R,
           i_s_L, lt_L, tttg_L, pt_L, lpt_L, bo_L, sa_L, lat_incl_L, med_incl_L, td_L, mis_L, cd_L, bp_L, ta_L)


def insall_salvati(sup_ar_pat, inf_pat, tub_tib):
    # Insall Salvati Ratio
    xtt, ytt, ztt = tub_tib
    tub_tib = ytt, ztt
    xsap, ysap, zsap = sup_ar_pat
    sup_ar_pat = ysap, zsap
    xip, yip, zip = inf_pat
    inf_pat = yip, zip
    pat = math.dist(sup_ar_pat, inf_pat)
    tendon = math.dist(inf_pat, tub_tib)
    ins_sal = tendon/pat
    print("Insall-Salvati Ratio")
    return ins_sal


def lateral_translation(pat_ant, pat_post, troch_sulc):
    x, y, z = pat_ant
    pat_ant = [x, y]
    pat_ant = np.asarray(pat_ant)
    x, y, z = pat_post
    pat_post = [x, y]
    pat_post = np.asarray(pat_post)
    x, y, z = troch_sulc
    troch_sulc = [x, y]
    troch_sulc = np.asarray(troch_sulc)
    pat_lat_trans = np.linalg.norm(np.cross(pat_ant-pat_post, pat_post-troch_sulc))/np.linalg.norm(pat_ant-pat_post)
    pat_lat_trans = pat_lat_trans * 0.7
    print("Lateral Translation Patella")
    return pat_lat_trans


def tt_tg(pcl_m, pcl_l, tub_tib, troch_sulc):
    xm, ym, zm = pcl_m
    xl, yl, zl = pcl_l
    x3, y3, z3 = tub_tib
    dx, dy = xl-xm, yl-ym
    det = dx*dx + dy*dy
    a = (dy*(y3-yl)+dx*(x3-xl))/det
    xtt, ytt = xl+a*dx, yl+a*dy
    tt = xtt, ytt

    x4, y4, z4 = troch_sulc
    b = (dy*(y4-yl)+dx*(x4-xl))/det
    xtg, ytg = xl+b*dx, yl+b*dy
    tg = xtg, ytg

    tttg = math.dist(tt, tg)
    tttg = tttg * 0.7
    print("TT-TG distance")
    return tttg


def pat_tilt(pat_m, pat_l, pcl_m, pcl_l):
    pat_width = pat_m-pat_l
    pcl = pcl_m-pcl_l
    unit_pcl = pcl/np.linalg.norm(pcl)
    unit_pat = pat_width/np.linalg.norm(pat_width)
    dot_product = np.dot(unit_pcl, unit_pat)
    angle = np.arccos(dot_product)
    pat_tilt = 180 * angle / np.pi
    print('Patellar Tilt')
    return pat_tilt


def lat_pat_tilt(pat_post, pat_l, cond_ant_l, cond_ant_m):
    lat_ridge = pat_post - pat_l
    cond_line = cond_ant_l - cond_ant_m
    unit_lat = lat_ridge / np.linalg.norm(lat_ridge)
    unit_cond = cond_line / np.linalg.norm(cond_line)
    dot_product = np.dot(unit_lat, unit_cond)
    angle = np.arccos(dot_product)
    lat_pat_tilt = 180 * angle / np.pi
    print("Lateral Patellar Tilt")
    return lat_pat_tilt


def bis_offset(troch_sulc, pcl_m, pcl_l, pat_l, pat_m):
    troch_sulc = np.asarray([troch_sulc[0], troch_sulc[1]])
    xm, ym, zm = pcl_m
    xl, yl, zl = pcl_l
    x3, y3 = troch_sulc
    dx, dy = xl-xm, yl-ym
    det = dx*dx + dy*dy
    a = (dy*(y3-yl)+dx*(x3-xl))/det
    xpcl, ypcl = xl+a*dx, yl+a*dy
    mid_pcl = xpcl, ypcl

    def line_intersection(line1, line2):
        xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
        ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

        def det(a, b):
            return a[0] * b[1] - a[1] * b[0]

        div = det(xdiff, ydiff)
        if div == 0:
            raise Exception('lines do not intersect')

        d = (det(*line1), det(*line2))
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div
        return x, y

    punt = tuple((line_intersection((mid_pcl, troch_sulc), (pat_l, pat_m))))
    d = pat_l[0]-pat_m[0]
    g = pat_l[0] - punt[0]
    bis_off = g/d
    print("Bisect Offset")
    return bis_off


def sulc_angle(cond_ant_l, cond_ant_m, troch_sulc):
    line_l = cond_ant_l - troch_sulc
    line_m = cond_ant_m - troch_sulc

    unit_l = line_l/np.linalg.norm(line_l)
    unit_m = line_m/np.linalg.norm(line_m)
    dot_product = np.dot(unit_l, unit_m)
    angle = np.arccos(dot_product)
    sulcus_angle = 180 * angle / np.pi
    print("Sulcus Angle")
    return sulcus_angle


def inclination(cond_ant_l, cond_ant_m, troch_sulc, pcl_m, pcl_l):

    lat_facet = cond_ant_l - troch_sulc
    med_facet = cond_ant_m - troch_sulc

    pcl = pcl_l - pcl_m

    unit_lat = lat_facet/np.linalg.norm(lat_facet)
    unit_med = med_facet/np.linalg.norm(med_facet)
    unit_pcl = pcl/np.linalg.norm(pcl)
    dot_product = np.dot(unit_lat, unit_pcl)
    angle = np.arccos(dot_product)
    lat_incl = 180 * angle / np.pi

    dot_product_med = np.dot(unit_med, unit_pcl)
    angle_med = np.arccos(dot_product_med)
    med_incl = 180*angle_med/np.pi
    print("lateral and medial inclination")
    return lat_incl, med_incl


def depth_troch(cond_ant_m, cond_ant_l, troch_sulc):
    xm, ym, zm = cond_ant_m
    xl, yl, zl = cond_ant_l
    x3, y3, z3 = troch_sulc
    troch_sulc = x3, y3
    dx, dy = xl-xm, yl - ym
    det = dx * dx + dy * dy
    a = (dy*(y3-yl)+dx*(x3-xl))/det
    xtd, ytd = xl+a*dx, yl+a*dy
    td = xtd, ytd

    troch_depth = math.dist(td, troch_sulc)
    troch_depth = troch_depth * 0.7
    print("Trochlear Depth")
    return troch_depth


def cd_bp_mis(sup_pat, inf_ar_pat, tib_ant_sup, tub_tib, tib_sup):
    xtt, ytt, ztt = tub_tib
    tub_tib = ytt, ztt
    xsap, ysap, zsap = sup_pat
    sup_pat = ysap, zsap
    xiap, yiap, ziap = inf_ar_pat
    inf_ar_pat = yiap, ziap
    xtas, ytas, ztas = tib_ant_sup
    tib_ant_sup = ytas, ztas

    pat_ar = math.dist(sup_pat, inf_ar_pat)
    pat_tib = math.dist(inf_ar_pat, tib_ant_sup)
    pat_tub = math.dist(inf_ar_pat, tub_tib)

    mod_is = pat_tub/pat_ar

    cat_dchmps = pat_tib/pat_ar

    a, b, tib_plat = np.asarray(tib_sup)
    pat_plat = inf_ar_pat[1]-tib_plat
    black_peel = pat_plat/pat_ar
    print("Modified Insall Salvati, Caton-Deschamps, Blackburne-Peele")
    return mod_is, cat_dchmps, black_peel


def troch_angle(cond_ant_m, cond_ant_l, pcl_m, pcl_l):
    ant = cond_ant_m - cond_ant_l
    pcl = pcl_m - pcl_l
    unit_pcl = pcl/np.linalg.norm(pcl)
    unit_ant = ant/np.linalg.norm(ant)
    dot_product = np.dot(unit_ant, unit_pcl)
    angle = np.arccos(dot_product)
    tr_angl = 180 * angle / np.pi
    print("Trochlear Angle")
    return tr_angl


def calculate_parameters(output_file, ids):
    workbook = xlsxwriter.Workbook(output_file)
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': True})
    first_line = ['ID',
                  'Insall Salvati Ratio R',
                  'Lateral Translation Patella R',
                  'TT-TG Distance R',
                  'Patellar Tilt R',
                  'Lateral Patellar Tilt R',
                  'Bisect Offset R',
                  'Sulcus Angle R',
                  'Lateral Inclination R',
                  'Medial Inclination R',
                  'Trochlear Depth R',
                  'Modified Insall Salvati R',
                  'Caton-Deschamps Ratio R',
                  'Blackburne-Peele Ratio R',
                  'Trochlear Angle R',
                  'Insall Salvati Ratio L',
                  'Lateral Translation Patella L',
                  'TT-TG Distance L',
                  'Patellar Tilt L',
                  'Lateral Patellar Tilt L',
                  'Bisect Offset L',
                  'Sulcus Angle L',
                  'Lateral Inclination L',
                  'Medial Inclination L',
                  'Trochlear Depth L',
                  'Modified Insall Salvati L',
                  'Caton-Deschamps Ratio L',
                  'Blackburne-Peele Ratio L',
                  'Trochlear Angle L'
                  ]
    for column, value in enumerate(first_line):
        worksheet.write(0, column, value, bold)

    file = "D:/TM Stage Resources/Stage 3 Resources/Sample data/data1.json"

    for row, patient_id in enumerate(ids):
        (i_s_R, lt_R, tttg_R, pt_R, lpt_R, bo_R, sa_R, lat_incl_R, med_incl_R, td_R, mis_R, cd_R, bp_R, ta_R,
         i_s_L, lt_L, tttg_L, pt_L, lpt_L, bo_L, sa_L, lat_incl_L, med_incl_L, td_L, mis_L, cd_L, bp_L, ta_L
         ) = knee_marker_analysis(file)
        worksheet.write(row + 1, 0, patient_id)
        worksheet.write(row + 1, 1, i_s_R)
        worksheet.write(row + 1, 2, lt_R)
        worksheet.write(row + 1, 3, tttg_R)
        worksheet.write(row + 1, 4, pt_R)
        worksheet.write(row + 1, 5, lpt_R)
        worksheet.write(row + 1, 6, bo_R)
        worksheet.write(row + 1, 7, sa_R)
        worksheet.write(row + 1, 8, lat_incl_R)
        worksheet.write(row + 1, 9, med_incl_R)
        worksheet.write(row + 1, 10, td_R)
        worksheet.write(row + 1, 11, mis_R)
        worksheet.write(row + 1, 12, cd_R)
        worksheet.write(row + 1, 13, bp_R)
        worksheet.write(row + 1, 14, ta_R)
        worksheet.write(row + 1, 15, i_s_L)
        worksheet.write(row + 1, 16, lt_L)
        worksheet.write(row + 1, 17, tttg_L)
        worksheet.write(row + 1, 18, pt_L)
        worksheet.write(row + 1, 19, lpt_L)
        worksheet.write(row + 1, 20, bo_L)
        worksheet.write(row + 1, 21, sa_L)
        worksheet.write(row + 1, 22, lat_incl_L)
        worksheet.write(row + 1, 23, med_incl_L)
        worksheet.write(row + 1, 24, td_L)
        worksheet.write(row + 1, 25, mis_L)
        worksheet.write(row + 1, 26, cd_L)
        worksheet.write(row + 1, 27, bp_L)
        worksheet.write(row + 1, 28, ta_L)
    workbook.close()


if __name__ == '__main__':
    # Run a test:
    test = "D:/TM Stage Resources/Stage 3 Resources/Sample data/data4.json"
    calculate_parameters('D:/test1.xlsx', [1])
    # knee_marker_analysis(test)
