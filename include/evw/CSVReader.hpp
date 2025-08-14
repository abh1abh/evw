#pragma once
#include <string>
#include <vector>

struct FinancialRow {
    int Year;
    std::string Metric;
    double Value;
};

class CSVReader {
public:
    CSVReader(const std::string& filename);

    std::vector<FinancialRow> read();

private:
    std::string filename_;
};
