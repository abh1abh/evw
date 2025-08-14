#include "evw/CSVReader.hpp"
#include <iostream>

int main (int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <csv-file>\n";
        return 1;
    }

    std::string filename = argv[1];
    CSVReader reader(filename);
    auto rows = reader.read();

    if (rows.empty()) {
        std::cerr << "No data read from file: " << filename << "\n";
        return 1;
    }

    for (const auto& row : rows) {
        std::cout << row.Year << " | "
                  << row.Metric << " | "
                  << row.Value << "\n";
    }

    return 0;

}