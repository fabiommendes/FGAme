#!/bin/sh

# Install FGAme
python setup.py install --user
echo ""
echo "------------------------------------------------------------------------"
echo "------------------------------------------------------------------------"

# Make docs
cd doc
make html
echo "------------------------------------------------------------------------"
echo "------------------------------------------------------------------------"

# Compress html documentation and save it back to FGAme's root 
cd build/html
rm -f html.zip
zip -r html.zip * > /dev/null
cd ..
cd ..
cd ..
mv doc/build/html/html.zip .
echo "Done!"

