import file_import
import controller
from plotting.ucc import CellCropper

a = file_import.import_files("*.dm3",output_filename='wing_test')
adv = controller.HighSeasAdventure(a)

#adv.plot_images()

adv.cell_cropper()

adv.plot_cells()

#print a.getNode('/cells','2int_63_bin')