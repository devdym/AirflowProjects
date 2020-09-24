from sqlalchemy import create_engine
from seislogAPI import digicourse
from seislogAPI import seal408
from seislogAPI import nav
from pandas import DataFrame


def scan_folder(basepath):
    project_path = []
    project_vessel_path = []
    project_vessel_data_path = []
    projects = []
    vessels = []
    all_res = {}

    # find all projects
    for project in basepath.iterdir():
        if project.is_dir():
            projects.append(project.name)
            project_path.append(basepath.joinpath(project.name))
            # print('Project {} at path {}'.format(str(projects[-1]), str(project_path[-1])))

    # find all vessels
    for project in project_path:
        for vessel in project.iterdir():
            if vessel.is_dir():
                project_vessel_path.append(vessel)
                vessels.append(vessel.name)
                # print('Vessel {} at path {}'.format(str(vessels[-1]), str(project_vessel_path[-1])))

    # find all result folders
    for data in project_vessel_path:
        for da in data.iterdir():
            project_vessel_data_path.append(da)
            # print('data folders {}'.format(project_vessel_data_path[-1]))

    # find all result files
    for results in project_vessel_data_path:
        for result in results.iterdir():
            data_dict = {}
            if result.is_file:
                data_dict['project_name'] = result.parent.parent.parent.name
                data_dict['vessel_name'] = result.parent.parent.name
                data_dict['result_name'] = result.parent.name
                data_dict['file_name'] = result.name
                data_dict['file_path'] = result
            all_res[str(result)] = data_dict

    return all_res


def logFiles_toMySql(data):
    """stores files path into MySQL

	Parameters
	----------
	data : Pandas DataFrame
		[description]
	"""

    df = DataFrame(data, columns=['file'])
    # create sqlalchemy engine
    engine = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}"
                           .format(user="usersql",
                                   pw="usersql",
                                   db="aurora_light"))
    df.to_sql('importLog', con=engine, if_exists='append', chunksize=1000, index=False)
