function [featureMean, featureStdv, zeroMean, zeroStdv] = histFeatureCountAnalysis(filePath)
    close all;


    table = readtable(filePath);

    correctDataFeatureCount = [];
    incorrectDataFeatureCount = [];
    zeroDataFeatureCount = [];

    correctDataFeatureCountDiff = [];
    incorrectDataFeatureCountDiff = [];
    zeroDataFeatureCountDiff = [];

    correctFeatureRatio = [];
    incorrectFeatureRatio = [];
    zeroDataFeatureRatio = [];

    dim = size(table);

    for ii = 1:dim(1)
       row = table(ii, :);

       if row.("ActualValue") == 0
            zeroDataFeatureCount = [zeroDataFeatureCount row.("Features")];
            zeroDataFeatureCountDiff = [zeroDataFeatureCountDiff row.("Features") - row.("SecondMostFeatures")];
            zeroDataFeatureRatio = [correctFeatureRatio row.("Features") / row.("ReferenceBillFeatures")];
       elseif row.("ActualValue") == row.("DetectedValue")
            correctDataFeatureCount = [correctDataFeatureCount row.("Features")];
            correctDataFeatureCountDiff = [correctDataFeatureCountDiff row.("Features") - row.("SecondMostFeatures")];
            correctFeatureRatio = [correctFeatureRatio row.("Features") / row.("ReferenceBillFeatures")];
       else
            incorrectDataFeatureCount = [incorrectDataFeatureCount row.("Features")];
            incorrectDataFeatureCountDiff = [incorrectDataFeatureCountDiff row.("Features") - row.("SecondMostFeatures")];
            incorrectFeatureRatio = [correctFeatureRatio row.("Features") / row.("ReferenceBillFeatures")];
       end
    end

    widthvalue = 10;

    histogram(correctDataFeatureCount,'BinWidth',widthvalue);

    hold on;
    histogram(incorrectDataFeatureCount,'BinWidth',widthvalue);
    histogram(zeroDataFeatureCount,'BinWidth',widthvalue);

    legend(["Correct","Incorrect","Non Currency"]);
    title("Feature Count");

    % widthvalue2 = 10;

    % figure;
    % histogram(correctDataFeatureCountDiff,'BinWidth',widthvalue2);

    % hold on;
    % histogram(incorrectDataFeatureCountDiff,'BinWidth',widthvalue2);
    % histogram(zeroDataFeatureCountDiff,'BinWidth',widthvalue2);

    % legend(["Correct","Incorrect","Non Currency"]);
    % title("Feature Difference");

    % widthvalue3 = 0.001;

    % figure;
    % histogram(correctFeatureRatio,'BinWidth',widthvalue3);

    % hold on;
    % histogram(incorrectFeatureRatio,'BinWidth',widthvalue3);
    % histogram(zeroDataFeatureRatio,'BinWidth',widthvalue3);

    % legend(["Correct","Incorrect","Non Currency"]);
    % title("Feature Ratio");

    featureMean = mean(correctDataFeatureCount);
    featureStdv = std(correctDataFeatureCount);
    zeroMean = mean(zeroDataFeatureCount);
    zeroStdv = std(zeroDataFeatureCount);

    max(zeroDataFeatureCount)
end