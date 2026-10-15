#import <Foundation/Foundation.h>
#import <Vision/Vision.h>
#import <AppKit/AppKit.h>

@interface OCRProcessor : NSObject
+ (NSDictionary *)processImage:(NSString *)filePath;
@end

@implementation OCRProcessor

+ (NSDictionary *)processImage:(NSString *)filePath {
    NSURL *url = [NSURL fileURLWithPath:filePath];
    NSImage *image = [[NSImage alloc] initWithContentsOfURL:url];
    if (!image) {
        return @{@"file": [filePath lastPathComponent], @"error": @"Could not load image"};
    }
    
    CGImageRef cgImage = [image CGImageForProposedRect:NULL context:nil hints:nil];
    if (!cgImage) {
        return @{@"file": [filePath lastPathComponent], @"error": @"Could not get CGImage"};
    }
    
    NSMutableArray *lines = [NSMutableArray array];
    
    VNImageRequestHandler *handler = [[VNImageRequestHandler alloc] initWithCGImage:cgImage options:@{}];
    VNRecognizeTextRequest *request = [[VNRecognizeTextRequest alloc] initWithCompletionHandler:^(VNRequest * _Nonnull req, NSError * _Nullable err) {
        if (err) return;
        NSArray *results = req.results;
        for (VNRecognizedTextObservation *obs in results) {
            VNRecognizedText *topCandidate = [[obs topCandidates:1] firstObject];
            if (topCandidate) {
                CGRect bbox = obs.boundingBox;
                [lines addObject:@{
                    @"text": topCandidate.string,
                    @"confidence": @(topCandidate.confidence),
                    @"x": @(bbox.origin.x),
                    @"y": @(bbox.origin.y),
                    @"w": @(bbox.size.width),
                    @"h": @(bbox.size.height)
                }];
            }
        }
    }];
    
    request.recognitionLevel = VNRequestTextRecognitionLevelAccurate;
    request.usesLanguageCorrection = YES;
    
    NSError *error = nil;
    [handler performRequests:@[request] error:&error];
    
    return @{
        @"file": [filePath lastPathComponent],
        @"lines": lines
    };
}

@end

int main(int argc, const char * argv[]) {
    @autoreleasepool {
        if (argc < 3) {
            printf("Usage: %s <input_dir> <output_json>\n", argv[0]);
            return 1;
        }
        
        NSString *inputDir = [NSString stringWithUTF8String:argv[1]];
        NSString *outputJson = [NSString stringWithUTF8String:argv[2]];
        
        NSFileManager *fm = [NSFileManager defaultManager];
        NSArray *files = [fm contentsOfDirectoryAtPath:inputDir error:nil];
        
        NSMutableArray *imageFiles = [NSMutableArray array];
        for (NSString *file in files) {
            NSString *ext = [[file pathExtension] lowercaseString];
            if ([ext isEqualToString:@"jpg"] || [ext isEqualToString:@"jpeg"] || [ext isEqualToString:@"png"] || [ext isEqualToString:@"webp"]) {
                [imageFiles addObject:[inputDir stringByAppendingPathComponent:file]];
            }
        }
        
        NSLog(@"Found %lu images to process...", (unsigned long)[imageFiles count]);
        
        NSMutableArray *allResults = [NSMutableArray arrayWithCapacity:[imageFiles count]];
        for (NSUInteger i = 0; i < [imageFiles count]; i++) {
            [allResults addObject:[NSNull null]];
        }
        
        dispatch_queue_t queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_HIGH, 0);
        dispatch_apply([imageFiles count], queue, ^(size_t index) {
            @autoreleasepool {
                NSString *path = imageFiles[index];
                NSDictionary *res = [OCRProcessor processImage:path];
                @synchronized(allResults) {
                    allResults[index] = res;
                }
                if (index % 25 == 0 || index == [imageFiles count] - 1) {
                    NSLog(@"Processed %zu / %lu cards", index + 1, (unsigned long)[imageFiles count]);
                }
            }
        });
        
        NSData *jsonData = [NSJSONSerialization dataWithJSONObject:allResults options:NSJSONWritingPrettyPrinted error:nil];
        [jsonData writeToFile:outputJson atomically:YES];
        NSLog(@"Saved OCR results to %@", outputJson);
    }
    return 0;
}
