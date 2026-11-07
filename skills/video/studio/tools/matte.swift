// scripts/matte.swift : cut the subject out of a still with the Mac's own subject detection (Vision), free and local.
// Usage: swift <skill>/scripts/matte.swift in.jpg out.png [maxWidth]   -> a PNG of the same shape whose alpha is the subject
import Foundation
import Vision
import CoreImage
import AppKit
let a = CommandLine.arguments
let inURL = URL(fileURLWithPath: a[1]), outURL = URL(fileURLWithPath: a[2]); let maxW = a.count > 3 ? Double(a[3])! : 2560
guard let img = CIImage(contentsOf: inURL) else { print("cannot read", a[1]); exit(1) }
let handler = VNImageRequestHandler(ciImage: img, options: [:]); let req = VNGenerateForegroundInstanceMaskRequest()
try handler.perform([req])
guard let obs = req.results?.first else { print("no subject found in", a[1]); exit(2) }
let mask = CIImage(cvPixelBuffer: try obs.generateScaledMaskForImage(forInstances: obs.allInstances, from: handler))
let f = CIFilter(name: "CIBlendWithMask")!
f.setValue(img, forKey: kCIInputImageKey); f.setValue(CIImage(color: CIColor(red: 0, green: 0, blue: 0, alpha: 0)).cropped(to: img.extent), forKey: kCIInputBackgroundImageKey); f.setValue(mask, forKey: kCIInputMaskImageKey)
var out = f.outputImage!.cropped(to: img.extent); let s = min(1.0, maxW / Double(img.extent.width))
if s < 1 { out = out.transformed(by: CGAffineTransform(scaleX: s, y: s)) }
try CIContext().writePNGRepresentation(of: out, to: outURL, format: .RGBA8, colorSpace: CGColorSpace(name: CGColorSpace.sRGB)!)
print(a[1], "->", a[2], "subjects:", obs.allInstances.count)
