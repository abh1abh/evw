#include "evw/CSVReader.hpp"
#include <fstream>
#include <sstream>
#include <iostream>

CSVReader::CSVReader(const std::string& filename)
    : filename_(filename) {}


std::vector<FinancialRow> CSVReader::read() {
    std::vector<FinancialRow> data;

    std::ifstream file(filename_);
    if (!file.is_open()) {
        std::cerr << "Failed to open file: " << filename_ << std::endl;
        return data;
    }

    std::string line;
    bool firstLine = true;

    while (std::getline(file, line)) {
        if(line.empty()) continue;

        std::stringstream ss(line);
        std::string yearStr, metricStr, valueStr;

        if (!std::getline(ss, yearStr, ',')) continue;
        if (!std::getline(ss, metricStr, ',')) continue;
        if (!std::getline(ss, valueStr, ',')) continue;

        if (firstLine) { 
            firstLine = false; 
            continue; 
        }

        FinancialRow row;

        try{
            row.Year = std::stoi(yearStr);
            row.Metric = metricStr;
            row.Value = std::stoi(valueStr);
        } catch (const std::exception& e){
            std::cerr << "Parse error: " << e.what() <<" in line: " << line << "\n";
            continue;
        }
        data.push_back(row);
    }

    file.close();    
    return data;
}